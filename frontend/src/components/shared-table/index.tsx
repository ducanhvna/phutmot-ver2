"use client";

import React from "react";
import {
  Table,
  TableContainer,
  TableHead,
  TableBody,
  TableRow,
  TableCell,
  Paper,
  Box
} from "@mui/material";

export type SharedTableColumn = {
  title: string;
  dataIndex?: string;
  key: string;
  width?: number;
  render?: (text: any, record: any) => React.ReactNode;
};

interface SharedTableProps<T> {
  dataSource: T[];
  columns: SharedTableColumn[];
  themeColor?: string;
}

const SharedTable = <T extends Record<string, any>>({
  dataSource,
  columns,
  themeColor = "#17a098"
}: SharedTableProps<T>) => {
  return (
    <Box sx={{ overflowX: "auto", minWidth: "100%" }}>
      <TableContainer component={Paper} sx={{ marginBottom: 4, minWidth: "800px" }}>
        <Table>
          <TableHead>
            <TableRow>
              {columns.map((column) => (
                <TableCell
                  key={column.key}
                  sx={{
                    backgroundColor: themeColor,
                    color: "white",
                    textAlign: "center",
                    width: column.width
                  }}
                >
                  {column.title}
                </TableCell>
              ))}
            </TableRow>
          </TableHead>
          <TableBody>
            {dataSource.map((record, index) => (
              <TableRow key={index}>
                {columns.map((column) => (
                  <TableCell
                    key={`${index}-${column.key}`}
                    sx={{ textAlign: "center" }}
                  >
                    {column.render
                      ? column.render(column.dataIndex ? record[column.dataIndex] : null, record)
                      : column.dataIndex
                      ? record[column.dataIndex]
                      : null}
                  </TableCell>
                ))}
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    </Box>
  );
};

export default SharedTable;
