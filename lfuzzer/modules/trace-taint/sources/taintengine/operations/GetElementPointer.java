package taintengine.operations;

import java.io.IOException;

import taintengine.NodeMapper;
import taintengine.handlers.helperclasses.ArrayIndexMapper;
import taintengine.handlers.helperclasses.EventSender;
import taintengine.handlers.helperclasses.StructureMapper;
import utils.LineInformation;
import utils.TaintType;

public class GetElementPointer extends Operation {
    /**
     * Creates an getElementPoitner operation with the given line information.
     * @param info the given line information
     */
    public GetElementPointer(LineInformation info) { super(info); }

    @Override
    public void propagateTaint(NodeMapper nodeMapper) {
        super.propagateTaint(nodeMapper);

        var address = Long.parseUnsignedLong(getOperands()[0].getValue());
        for (var op : getOperandNames()) {
            var tntVec = nodeMapper.getTaintForName(op);
            if (tntVec != null && !tntVec.getTaint(0).isEmpty()) {
                var tnt = tntVec.getTaint(0);
                // for the moment we only taint tables with strconst taints (assuming those are the writes to a lookup table)
                // later we might also want to use this for semantic checks where we will also have to taint
                if (tnt.hasTaintType(TaintType.STRCONST)) {
                    nodeMapper.taintTablePointer(address, tntVec.getTaint(0));
                }
            }
        }
    }

    // for a GEP the structure mapper has to save the name of the variable together with the name of the accesses field element.
    @Override
    public void handleStructureSendFieldAccess(StructureMapper structureMapper, NodeMapper nodeMapper, EventSender eventSender) {
        // a pointer to a structure
        if (getOperands().length < 3) {
            return;
        }
        // TODO it might be the case, that multi dereferencing leads to a cascade of dereferencings
        structureMapper.mapLocalToElement(getNewNodeName(), getOperands()[0].getType(), extractValues(getOperands()[2].getValue())[0]);
    }

    @Override
    public void handleArrayAccess(NodeMapper nodeMapper, EventSender eventSender, ArrayIndexMapper arMapper) throws IOException {
        super.handleArrayAccess(nodeMapper, eventSender, arMapper);
        // if "[" is contained, then an element from an array is taken
        if (getOperands()[0].getType().contains("[")) {
            // the third operand defines the index
            arMapper.setArrayIndex(info.getAssignedRegisterName(), Integer.parseInt(getOperands()[2].getValue()));
            arMapper.setAccessedArray(info.getAssignedRegisterName(), getOperands()[0].getValue());
        }
    }

    @Override
    public void handleBinOperation(NodeMapper nodeMapper, EventSender eventSender) throws IOException {
        var address = Long.parseUnsignedLong(getOperands()[0].getValue());
        for (var op : getOperandNames()) {
            var opTaint = nodeMapper.getTaintForName(op);
            // if a tainted value is used for a loookup and the lookup is not done by a strconstant, then we need to check if we have taints attached to the address
            if (opTaint != null && !opTaint.isEmpty() && !opTaint.getTaint(0).hasTaintType(TaintType.STRCONST)) {
                var tnts = nodeMapper.getTablePointerTaints(address);
                if (tnts.length != 0) {
                    eventSender.tableLookup(opTaint.getTaint(0), tnts);
                }
            }
        }
    }
}
