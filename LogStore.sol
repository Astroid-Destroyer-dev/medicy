// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

contract LogStore {
    struct Log {
        address sender;
        uint256 blockTimestamp; // when tx was mined
        string doctorName;
        string reason;
        string patientId;
        uint256 logTime; // arbitrary time field (e.g., appointment time)
        string message;
    }

    Log[] public logs;

    event LogAdded(
        address indexed sender,
        uint256 blockTimestamp,
        string doctorName,
        string reason,
        string patientId,
        uint256 logTime,
        string message,
        uint256 index
    );

    function addLog(
        string calldata doctorName,
        string calldata reason,
        string calldata patientId,
        uint256 logTime,
        string calldata message
    ) external returns (uint256) {
        logs.push(Log(msg.sender, block.timestamp, doctorName, reason, patientId, logTime, message));
        uint256 idx = logs.length - 1;
        emit LogAdded(msg.sender, block.timestamp, doctorName, reason, patientId, logTime, message, idx);
        return idx;
    }

    function getLog(uint256 index)
        external
        view
        returns (
            address,
            uint256,
            string memory,
            string memory,
            string memory,
            uint256,
            string memory
        )
    {
        Log storage l = logs[index];
        return (l.sender, l.blockTimestamp, l.doctorName, l.reason, l.patientId, l.logTime, l.message);
    }

    function count() external view returns (uint256) {
        return logs.length;
    }
}
