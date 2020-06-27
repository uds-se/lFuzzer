package taintengine.operations;

import taintengine.NodeMapper;
import taintengine.handlers.helperclasses.ArrayIndexMapper;
import taintengine.handlers.helperclasses.EventSender;
import taintengine.handlers.helperclasses.TokenManager;
import utils.LineInformation;
import utils.Operand;
import utils.TaintType;

import java.io.IOException;

public class IsDigit extends Operation {
    public IsDigit(LineInformation info) {
        super(info);
    }

    @Override
    public void propagateTaint(NodeMapper nodeMapper) {
        super.propagateTaint(nodeMapper);
        newNode = info.getAssignedRegisterName();
    }

    @Override
    public void handleBinOperation(NodeMapper nodeMapper, EventSender eventSender) throws IOException {
        Operand value = getOperands()[0];
        var taint = nodeMapper.getTaintForName(value.getName());
        if (taint != null && !taint.isEmpty()) {
            eventSender.strchr(value.getValue(), "0123456789", taint.getTaint(0));
        }
    }

    @Override
    public void handleArrayAccess(NodeMapper nodeMapper, EventSender eventSender, ArrayIndexMapper arMapper) throws IOException {
        // Intentionally left blank
    }

    @Override
    public void handleToken(NodeMapper nodeMapper, TokenManager tokenManager, EventSender eventSender) {
        //TODO not tested yet
        var taint = nodeMapper.getTaintForName(getOperands()[0].getName());
        if (taint != null && !taint.isEmpty() && !taint.getTaint(0).hasTaintType(TaintType.TOKEN)) {
            tokenManager.markLexing(info.getFunction());
        }
    }
}
