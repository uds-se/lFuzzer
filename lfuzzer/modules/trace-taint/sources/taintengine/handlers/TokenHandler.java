package taintengine.handlers;

import taintengine.NodeMapper;
import taintengine.handlers.helperclasses.EventSender;
import taintengine.handlers.helperclasses.TokenManager;
import taintengine.operations.Operation;

public class TokenHandler extends OperationHandler {
    /***
     * Takes care of the generation of token taints. This handler is specifically designed to detect usages of enums, e.g. in assignments,
     * and attach taints to those enums from previous comparisons that used taints.
     */

    private final TokenManager tokenManager;
    private EventSender eventSender;

    public TokenHandler(EventSender eventSender) {
        this.eventSender = eventSender;
        tokenManager = new TokenManager();
    }

    @Override
    public void handleOperation(Operation operation, NodeMapper nodeMapper) {
        operation.handleToken(nodeMapper, tokenManager, eventSender);
    }
}
