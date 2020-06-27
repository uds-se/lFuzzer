package taintengine.operations;

import taintengine.NodeMapper;
import utils.LineInformation;

public class GlobalPrint extends Operation {

    /**
     * This operation is used to get for each global value the memory location it lies in.
     * @param info
     */
    public GlobalPrint(LineInformation info) {
        super(info);
    }

    @Override
    public void propagateTaint(NodeMapper nodeMapper) {
        for (var op : getOperands()) {
            if (op.getName().contains(".str")) {
                nodeMapper.taintGlobal(op.getName(), Long.parseLong(op.getValue()));
            }
        }
    }
}
