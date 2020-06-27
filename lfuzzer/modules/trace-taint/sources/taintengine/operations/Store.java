package taintengine.operations;

import taintengine.NodeMapper;
import taintengine.Taint;
import taintengine.TaintVector;
import taintengine.handlers.helperclasses.ArrayIndexMapper;
import taintengine.handlers.helperclasses.EventSender;
import taintengine.handlers.helperclasses.StructureMapper;
import taintengine.handlers.helperclasses.TokenManager;
import utils.LineInformation;
import utils.TaintType;

import java.io.IOException;
import java.util.Optional;

public class Store extends Operation {
    /**
     * Creates a Store operation with the given line information.
     * @param info the line information
     */
    public Store(LineInformation info) { super(info); }

    @Override
    public String[] getOperandNames() {
        return new String[]{getOperands()[0].getName()};
    }

    private Long getStoreTo() {
        // this part of the operator is always an address and therefore a long
        return Long.parseLong(getOperands()[1].getValue());
    }

    @Override
    public void propagateTaint(NodeMapper nodeMapper) {
        // store even if no taint exists for the source value, this may overwrite old taints that are in the memory cells
        // overwriting such olds taints is important since the actual value in the cell is also overwritten when storing
        // an untainted value
        //		if (!nodeMapper.existsTaintForName(this.getOperandNames()[0])) {
        //			this.newNode = this.getOperands()[1].getName();
        //			return;
        //		}
        //		System.out.println(nodeMapper.getTaintForName(this.getOperandNames()[0]));
        // tmp should have existed at this point, so check the vector that is stored at this point
        nodeMapper.addAddressTaint(getStoreTo(), getOperandNames()[0], getOperands()[0].getByteSizeUnderlyingType() / getOperands()[0].getVectorLength());
        newNode = getOperands()[1].getName();
    }

    @Override
    public void handleStructureSendFieldAccess(StructureMapper structureMapper, NodeMapper nodeMapper, EventSender eventSender) throws IOException {
        // check whether the pointer points to a field
        String structureName = getOperands()[1].getName();
        String fieldName = structureMapper.getFieldForLocal(structureName);
        if (fieldName == null) {
            return;
        }

        // if pointer points to a field, check whether the stores stores tainted data
        TaintVector fieldTaint = nodeMapper.getTaintForName(getOperands()[0].getName());
        // tv needs to be non null, if it is null, then there as no value initially
        if ((fieldTaint != null) && !fieldTaint.isEmpty()) {
            eventSender.fieldAccess(structureMapper.getStructureNameForLocal(structureName), fieldName, true, fieldTaint);
        }
    }

    @Override
    public void handleArrayAccess(NodeMapper nodeMapper, EventSender eventSender, ArrayIndexMapper arMapper) throws IOException {
        // for the store operation the memory is already allocated
        super.handleArrayAccess(nodeMapper, eventSender, arMapper);

        Long index = arMapper.getIndexForName(newNode);
        // if it was not mapped there was no array access for this variable
        if (index == null) {
            return;
        }

        eventSender.arrayWrite(index, Long.parseLong(arMapper.getAccessForName(newNode)), nodeMapper.getTaintForName(getOperands()[0].getName()), nodeMapper.getTaintForName(newNode));
    }

    @Override
    public void handleToken(NodeMapper nodeMapper, TokenManager tokenManager, EventSender eventSender) {
        if ("Constant".equals(getOperands()[0].getName()) && "i32".equals(getOperands()[0].getType())) {
            tokenManager.getValue().ifPresent(val -> tokenManager.getTnt().ifPresent(tnt -> {
                nodeMapper.addAddressTaint(getStoreTo(), new TaintVector(tnt), 4);
                eventSender.tokenStore(val, getOperands()[0].getValue(), tnt);
            }));
        } else {
            // check if a value with a token taint is stored and if so report the store
            var tnt1 = nodeMapper.getTaintForName(getOperandNames()[0]);
            boolean used = tokenManager.getUsed();
            var tokenManagerValue = tokenManager.getValue();
            var tokenManagerTnt = tokenManager.getTnt();
            if (tokenManagerValue.isPresent() && tokenManagerTnt.isPresent()) {
                if (tnt1 != null && !tnt1.isEmpty() && tnt1.getTaint(0).hasTaintType(TaintType.TOKEN)) {
                    nodeMapper.addAddressTaint(getStoreTo(), new TaintVector(tokenManagerTnt.get()), 4);
                    eventSender.tokenStore(tokenManagerValue.get(), getOperands()[0].getValue(), tokenManagerTnt.get());
                } else {
                    //in this case the token was not used, so set it to the value it was before
                    tokenManager.setUsed(used);
                }
            }
        }
    }

}
