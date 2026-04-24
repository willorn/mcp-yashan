package io.yashan.mcp;

import java.nio.charset.StandardCharsets;
import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.ResultSet;
import java.sql.ResultSetMetaData;
import java.sql.Statement;
import java.util.Base64;

public class SqlExecutorMain {
    public static void main(String[] args) {
        if (args.length < 5) {
            System.out.println("SUCCESS:false");
            System.out.println("ERROR:Usage: <sql> <maxRows> <jdbcUrl> <user> <password>");
            return;
        }

        String sql = args[0];
        int maxRows = Integer.parseInt(args[1]);
        String jdbcUrl = args[2];
        String user = args[3];
        String password = args[4];
        long startTime = System.currentTimeMillis();

        try {
            Class.forName("com.yashandb.jdbc.Driver");

            try (
                Connection conn = DriverManager.getConnection(jdbcUrl, user, password);
                Statement stmt = conn.createStatement()
            ) {
                stmt.setMaxRows(maxRows);
                boolean isResultSet = stmt.execute(sql);

                if (isResultSet) {
                    try (ResultSet rs = stmt.getResultSet()) {
                        ResultSetMetaData metaData = rs.getMetaData();
                        int columnCount = metaData.getColumnCount();

                        System.out.println("COLUMNS:" + columnCount);
                        for (int i = 1; i <= columnCount; i++) {
                            System.out.println("COL:" + metaData.getColumnName(i));
                        }

                        int rowCount = 0;
                        while (rs.next() && rowCount < maxRows) {
                            StringBuilder row = new StringBuilder("ROW_B64:");
                            for (int i = 1; i <= columnCount; i++) {
                                if (i > 1) {
                                    row.append("|");
                                }

                                Object value = rs.getObject(i);
                                if (value == null) {
                                    row.append("NULL");
                                } else {
                                    row.append(
                                        Base64.getEncoder().encodeToString(
                                            value.toString().getBytes(StandardCharsets.UTF_8)
                                        )
                                    );
                                }
                            }

                            System.out.println(row);
                            rowCount++;
                        }

                        System.out.println("ROW_COUNT:" + rowCount);
                    }
                } else {
                    int updateCount = stmt.getUpdateCount();
                    System.out.println("UPDATE_COUNT:" + updateCount);
                }
            }

            System.out.println("SUCCESS:true");
        } catch (Exception e) {
            System.out.println("SUCCESS:false");
            System.out.println("ERROR:" + (e.getMessage() == null ? e.toString() : e.getMessage()));
        }

        System.out.println("EXEC_TIME:" + (System.currentTimeMillis() - startTime));
    }
}
