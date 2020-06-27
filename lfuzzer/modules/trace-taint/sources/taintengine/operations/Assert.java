package taintengine.operations;

import taintengine.NodeMapper;
import taintengine.handlers.helperclasses.EventSender;
import utils.LineInformation;

import java.io.IOException;

public class Assert extends Operation {

    /**
     * processes the trace information of the call to the assert function of C.
     * @param info the trace information
     */
    public Assert(LineInformation info) {
        super(info);
    }

    @Override
    public void handleBinOperation(NodeMapper nodeMapper, EventSender eventSender) throws IOException {
        eventSender.assertCall();
    }
}
