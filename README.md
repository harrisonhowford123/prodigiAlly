# prodigiAlly
Remote barcode tracking software for windows/mac systems that connects and updates and to local server program



UPDATE employee_info
SET AdminPrivs = json_insert(
    COALESCE(AdminPrivs, '[]'),
    '$[' || json_array_length(COALESCE(AdminPrivs, '[]')) || ']',
    'pulse'
)
WHERE employeeName = 'Harry Howford';
