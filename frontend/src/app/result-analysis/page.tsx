"use client";

import React from "react";
import {
  Card,
  CardContent,
  CardHeader,
  Grid,
  Typography,
  Box
} from "@mui/material";
import EmojiEventsIcon from '@mui/icons-material/EmojiEvents'; // Icon kết quả học tập ở giữa

// Typography variants will be used directly

const COLORS = ["#FF6384", "#36A2EB", "#FFCE56", "#FF9F40"];



// Custom function để hiển thị nhãn phần trăm bên trong hoặc ngoài
// const renderCustomizedLabel = (props) => {
//   const { x, y, value } = props;
//   if (typeof value !== "number" || typeof x !== "number" || typeof y !== "number") return null;

//   return value >= 20 ? (
//     <text x={x} y={y} fill="#fff" textAnchor="middle" dominantBaseline="central" fontSize={14}>
//       {value}%
//     </text>
//   ) : (
//     <text x={x + 30} y={y} fill="#000" textAnchor="start" fontSize={14}>
//       {value}%
//     </text>
//   );
// };

export default function ResultAnalysisPage() {
  return (
    <Box sx={{ padding: 2.5 }}>
      <Typography variant="h2">結果分析</Typography>
      <Typography variant="h3">児童生徒の学習意識調査</Typography>

      <Typography variant="body1" sx={{ mt: 2, mb: 3 }}>
        これは小学校・中学校の学習状況を分析するための調査結果です。
        各教科の理解度や興味・関心についてのデータを視覚的に表示します。
      </Typography>

      {/* Pie Chart groups */}
      {/* {dummyData.map((group, index) => (
        <Box key={index} sx={{ mt: 5 }}>
          <Typography variant="h3">{group.groupTitle}</Typography>
          <Grid container spacing={2}>
            {group.charts.map((chart, idx) => (
              <Grid item key={idx} xs={12} sm={6} md={3} lg={3}>
                <Card elevation={2}>
                  <CardHeader title={chart.title} />
                  <CardContent>
                    <PieChart width={250} height={250}>
                      <Pie data={chart.data} cx="50%" cy="50%" outerRadius={100} fill="#8884d8" dataKey="value">
                        {chart.data.map((entry, id) => (
                          <Cell key={`cell-${id}`} fill={COLORS[id % COLORS.length]} />
                        ))}
                        <LabelList dataKey="value" content={(props) => renderCustomizedLabel(props as LabelProps)} />
                      </Pie>
                      <Tooltip />
                    </PieChart>
                  </CardContent>
                </Card>
              </Grid>
            ))}
          </Grid>
        </Box>
      ))} */}

      {/* Additional information section (4 cards + center icon) */}
      {/* <Grid container spacing={2} sx={{ mt: 5 }} justifyContent="center" alignItems="center">
        {dummyData[0].charts.map((card, index) => (
          <Grid item key={index} xs={12} sm={6} md={2} lg={2}>
            <Card sx={{ textAlign: "center", p: 2 }} elevation={2}>
              <CardHeader title={card.title} titleTypographyProps={{ variant: 'h6' }} />
              <CardContent>
                <Typography variant="body2" color="text.secondary">
                  {card.data.map((d) => d.name + ": " + d.value + "%").join(", ")}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        ))} */}
        {/* Center icon */}
        {/* <Grid item xs={12} sm={6} md={2} lg={2} sx={{ display: "flex", justifyContent: "center", alignItems: "center" }}>
          <EmojiEventsIcon sx={{ fontSize: 60, color: "#FFD700" }} />
        </Grid>
      </Grid> */}
    </Box>
  );
}
