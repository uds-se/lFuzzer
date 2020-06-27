package taintengine.operations;

import taintengine.NodeMapper;
import taintengine.Taint;
import taintengine.TaintVector;
import taintengine.handlers.helperclasses.EventSender;
import taintengine.handlers.helperclasses.TokenManager;
import utils.LineInformation;
import utils.Opcode;
import utils.Operand;
import utils.Predicate;
import utils.TaintType;
import utils.Utils;

import java.io.IOException;

public class BinOperation extends GenericOperation {

    /**
     * Create a sign extension operation with the given line information.
     * @param info
     */
    public BinOperation(LineInformation info) {
        super(info);
    }

    @Override
    public void propagateTaint(NodeMapper nodeMapper) {
        newNode = info.getAssignedRegisterName();
//        var tnt1 = nodeMapper.getTaintForName(info.getOperands()[0].getName());
//        var tnt2 = nodeMapper.getTaintForName(info.getOperands()[1].getName());
        // TODO in future have some better integration for taint types, for the moment we do not propagate strlen taints
        // over calculations
//        if ((tnt1 != null) && tnt1.getTaint(0).hasTaintType(TaintType.STRLEN) ||
//                (tnt2 != null) && tnt2.getTaint(0).hasTaintType(TaintType.STRLEN)) {
        var result = info.getAssignedRegister();
        nodeMapper.addLocal(result.getName(),
                getOperandNames(),
                result.getVectorLength(),
                result.getByteSizeUnderlyingType(),
                TaintVector::unionIntoFull);

        // this is a special case in which very likely the length of an array or string is taken
        // i.e. this is a substitution on addresses with tainted content
        handleStrlen(nodeMapper);
    }

    private void handleStrlen(NodeMapper nodeMapper) {
        if (info.getOpcode() == Opcode.SUB) {
            // address1 is the address of the first character behind the string if it is a strlen calculation operation
            long address1 = Long.parseUnsignedLong(getOperands()[0].getValue()) - 1;
            var tnt1 = nodeMapper.getTaintForAddress(address1, 1);
            long address2 = Long.parseUnsignedLong(getOperands()[1].getValue());
            var tnt2 = nodeMapper.getTaintForAddress(address2, 1);
            int numberOfBytes = (int) (address1 - address2);

            // if one of the taints is not empty we are looking at a substraction which includes a pointer to a tainted value
            // therefore we can assume that this is an operation to determine a strlen
            // also we need to reduce noise by only considering a small number of bytes
            if (!(tnt1[0].isEmpty() || tnt2[0].isEmpty())) {
                // TODO in future one can check if all bytes are tainted between the two addresses (off by one allowed)
                // address2 is the smaller address as you substract the smaller address from the larger
                var newTaint = nodeMapper.getTaintsForAddress(address2, 1, numberOfBytes + 1);
                newTaint.forEach(tnt -> tnt.addTaintType(TaintType.STRLEN));
                newTaint = TaintVector.unionIntoFull(new TaintVector(1, info.getAssignedRegister().getByteSizeUnderlyingType()), newTaint);
                Taint[] tnts = {newTaint.getTaint(0)};
                nodeMapper.addTaintForLocal(info.getAssignedRegisterName(), tnts);
            }
        }
    }

    @Override
    public void handleBinOperation(NodeMapper nodeMapper, EventSender eventSender) throws IOException {
        if (getOperands().length < 3) {
            //we only look at binops atm
            return;
        }

        Operand assignedRegister = info.getAssignedRegister();
        Operand operand1 = info.getOperands()[0];
        Operand operand2 = info.getOperands()[1];
        Operand operator = info.getOperands()[2];
        eventSender.binOperation(Integer.parseInt(operator.getValue()),
                                 operand1.getValue(),
                                 operand2.getValue(),
                                 nodeMapper.getTaintForName(assignedRegister.getName()),
                                 nodeMapper.getTaintForName(operand1.getName()),
                                 nodeMapper.getTaintForName(operand2.getName()));
    }

    @Override
    public void handleToken(NodeMapper nodeMapper, TokenManager tokenManager, EventSender eventSender) {
        Operand operand1 = info.getOperands()[0];
        Operand operand2 = info.getOperands()[1];
        // only report comparisons if both are i32 as tokens are normal integers
        if (info.getOpcode() == Opcode.ICMP && "i32".equals(operand1.getType()) && "i32".equals(operand2.getType())) {
            tokenManagerUpdate(nodeMapper, tokenManager);
            var tnt1 = nodeMapper.getTaintForName(operand1.getName());
            var tnt2 = nodeMapper.getTaintForName(operand2.getName());
            eventSender.tokenCompare(operand1.getValue(),
                    operand2.getValue(),
                    tnt1 != null ? tnt1.getTaint(0) : null,
                    tnt2 != null ? tnt2.getTaint(0) : null, tokenManager);
        } else {
            if ("Constant".equals(operand1.getName()) && "i32".equals(operand1.getType()) ||
                    "Constant".equals(operand2.getName()) && "i32".equals(operand2.getType())) {
                tokenManagerUpdate(nodeMapper, tokenManager);
                tokenManager.getTnt().ifPresent(tnt -> nodeMapper.addTaintForLocal(info.getAssignedRegisterName(), tnt));
            }
        }
    }

    /**
     * For arithmetic expressions check if a token is involved and if not update the {@link TokenManager}.
     * @param nodeMapper the nodemapper
     * @param tokenManager the tokenmanager
     */
    private void tokenManagerUpdate(NodeMapper nodeMapper, TokenManager tokenManager) {
        var tnt1 = nodeMapper.getTaintForName(getOperandNames()[0]);
        var tnt2 = nodeMapper.getTaintForName(getOperandNames()[1]);
        if (tnt1 != null && !tnt1.isEmpty() && !tnt1.getTaint(0).hasTaintType(TaintType.TOKEN)) {
            if (info.getOpcode() == Opcode.ICMP) {
                Taint taint = tnt1.getTaint(0);
                tokenManager.markLexing(info.getFunction());
                tokenManager.setTaint(getOperands()[0].getValue(), taint);
            } else {
                // clean token if the comparison was not successful but contained taints
                tokenManager.clean();
            }
        } else {
            if (tnt2 != null && !tnt2.isEmpty() && !tnt2.getTaint(0).hasTaintType(TaintType.TOKEN)) {
                if (getOperands()[0].getValue().equals(getOperands()[1].getValue())) {
                    Taint taint = tnt2.getTaint(0);
                    tokenManager.markLexing(info.getFunction());
                    tokenManager.setTaint(getOperands()[1].getValue(), taint);
                } else {
                    // clean token if the comparison was not successful but contained taints
                    tokenManager.clean();
                }
            }
        }
    }
}
