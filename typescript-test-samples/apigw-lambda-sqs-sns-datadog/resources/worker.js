"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
const axios_1 = require("axios");
const delay_1 = require("./delay");
exports.main = async function (event) {
    for (let i = 0; i < 5; i++) {
        await axios_1.default.get('https://datadoghq.com');
        await (0, delay_1.default)(15);
    }
    console.log('SQS worker successfully received event:', event);
};
//# sourceMappingURL=data:application/json;base64,eyJ2ZXJzaW9uIjozLCJmaWxlIjoid29ya2VyLmpzIiwic291cmNlUm9vdCI6IiIsInNvdXJjZXMiOlsid29ya2VyLnRzIl0sIm5hbWVzIjpbXSwibWFwcGluZ3MiOiI7O0FBQ0EsaUNBQTBCO0FBQzFCLG1DQUE0QjtBQUU1QixPQUFPLENBQUMsSUFBSSxHQUFHLEtBQUssV0FBVSxLQUFlO0lBQzNDLEtBQUssSUFBSSxDQUFDLEdBQUMsQ0FBQyxFQUFFLENBQUMsR0FBRyxDQUFDLEVBQUUsQ0FBQyxFQUFFLEVBQUU7UUFDdEIsTUFBTSxlQUFLLENBQUMsR0FBRyxDQUFDLHVCQUF1QixDQUFDLENBQUM7UUFDekMsTUFBTSxJQUFBLGVBQUssRUFBQyxFQUFFLENBQUMsQ0FBQztLQUNqQjtJQUNILE9BQU8sQ0FBQyxHQUFHLENBQUMseUNBQXlDLEVBQUUsS0FBSyxDQUFDLENBQUE7QUFDL0QsQ0FBQyxDQUFBIiwic291cmNlc0NvbnRlbnQiOlsiaW1wb3J0IHsgU1FTRXZlbnQgfSBmcm9tIFwiYXdzLWxhbWJkYVwiO1xuaW1wb3J0IGF4aW9zIGZyb20gJ2F4aW9zJztcbmltcG9ydCBkZWxheSBmcm9tICcuL2RlbGF5JztcblxuZXhwb3J0cy5tYWluID0gYXN5bmMgZnVuY3Rpb24oZXZlbnQ6IFNRU0V2ZW50KTogUHJvbWlzZTx2b2lkPiB7XG4gIGZvciAobGV0IGk9MDsgaSA8IDU7IGkrKykge1xuICAgICAgYXdhaXQgYXhpb3MuZ2V0KCdodHRwczovL2RhdGFkb2docS5jb20nKTtcbiAgICAgIGF3YWl0IGRlbGF5KDE1KTtcbiAgICB9XG4gIGNvbnNvbGUubG9nKCdTUVMgd29ya2VyIHN1Y2Nlc3NmdWxseSByZWNlaXZlZCBldmVudDonLCBldmVudClcbn1cblxuIl19