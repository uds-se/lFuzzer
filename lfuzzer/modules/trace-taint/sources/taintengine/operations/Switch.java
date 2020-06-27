package taintengine.operations;

import taintengine.NodeMapper;
import taintengine.Taint;
import taintengine.TaintVector;
import taintengine.handlers.helperclasses.EventSender;
import taintengine.handlers.helperclasses.TokenManager;
import utils.LineInformation;
import utils.Operand;
import utils.TaintType;

import java.io.IOException;
import java.util.LinkedList;

public class Switch extends Operation {
    /**
     * Creates a switch operation with the given line information.
     * @param info
     */
    public Switch(LineInformation info) { super(info); }

    @Override
    public void handleBranch(NodeMapper nodeMapper, EventSender eventSender) throws IOException {
        eventSender.branch(nodeMapper.getTaintForName(getOperands()[0].getName()));
    }

    @Override
    public void handleBinOperation(NodeMapper nodeMapper, EventSender eventSender) throws IOException {
        Operand[] operands = getOperands();
        Operand switchRegister = operands[0];
        TaintVector taintSwitchRegister = getTaintVector(nodeMapper, switchRegister);
        if (taintSwitchRegister == null) return;

        LinkedList<String> values = getValues(operands);
        eventSender.swtch(switchRegister.getValue(), values.toArray(new String[0]), taintSwitchRegister.getTaint(0));
        //TODO add token read here later
    }

    private LinkedList<String> getValues(Operand[] operands) {
        var values = new LinkedList<String>();
        for (int i = 1; i < operands.length ; i++) {
            Operand operand = operands[i];
            if ("label".equals(operand.getType())) {
                continue;
            }

            values.add(operand.getValue());
        }
        return values;
    }

    private TaintVector getTaintVector(NodeMapper nodeMapper, Operand switchRegister) {
        TaintVector taintSwitchRegister = nodeMapper.getTaintForName(switchRegister.getName());

        if (taintSwitchRegister == null || taintSwitchRegister.isEmpty()) {
            // at this point the character that is used for comparison is not tainted and therefore of no interest for us
            return null;
        }
        return taintSwitchRegister;
    }

    @Override
    public void handleToken(NodeMapper nodeMapper, TokenManager tokenManager, EventSender eventSender) {
        TaintVector taintVector = getTaintVector(nodeMapper, getOperands()[0]);
        if (taintVector != null) {
            Taint switchTaint = taintVector.getTaint(0);
            tokenManager.setTaint(getOperands()[0].getValue(), switchTaint);
            // check if tokentaint is present, otw. there is nothing to send
            if (switchTaint.hasTaintType(TaintType.TOKEN)) {
                LinkedList<String> values = getValues(getOperands());
                for (var value : values) {
                    eventSender.tokenCompare(getOperands()[0].getValue(), value, switchTaint, null, tokenManager);
                }
            } else {
                if (switchTaint != null && !switchTaint.isEmpty()) {
                    //TODO test
                    tokenManager.markLexing(info.getFunction());
                }
            }
        }
    }
}
