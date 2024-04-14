import React, { useState } from "react";
import { Grid, Typography } from "@mui/material";
import MyAppBar from "./components/AppBar/AppBar";
import BarPlot from "./components/BarPlot/BarPlot";
import { DataPoint } from "./constants";

const sse = new EventSource("https://lehre.bpm.in.tum.de/ports/9998/sse");
// const sse = new EventSource("http://[::1]:9998/stream");

function App() {
  const [data, setData] = useState<DataPoint[]>([]);

sse.onmessage = (e) => {
  if (e.data === '[]') {
    return;
  } 

  const message: DataPoint[] = JSON.parse(JSON.parse(e.data));
  console.log((new Date()).toISOString().slice(0, 19).replace('T', ' '));
  console.log('New Values: ');
  console.log(message);
  if (data.length === 0 && message) {
    const filtered: DataPoint[] = []
    message.forEach(entry => {
      filtered.push({
	...entry,
        Discount: entry.Discount ? entry.Discount : 0
      });
    })
    setData(filtered);
    return;
  }
  if (message) {
    const pricesMap = new Map<string, number>();
    const oldData = [...data];
    data.forEach((entry) => pricesMap.set(entry.SKU, entry.Discount));
    console.log('old values:');
    console.log(pricesMap)
    message.forEach((entry, index) => {
      const oldIndex = data.findIndex((p) => p.SKU === entry.SKU);
      if (oldIndex !== -1) {
        oldData[oldIndex].Discount = entry.Discount
      } else {
          oldData.push({
          SKU: entry.SKU,
          Discount: entry.Discount,
          Timestamp: entry.Timestamp
          });
      }
    });

  console.log('Combinend Data')
  console.log(oldData)

  setData(oldData);
  console.log('-------------------');
  }
};


  return (
    <div style={{ width: "100%", height: "100%" }}>
      <MyAppBar />
      <Grid sx={{ marginTop: "10px", marginLeft: "10px" }} container>
        <Grid item xs={12}>
          <Typography variant="h4">Price Tracker</Typography>
        </Grid>
        <Grid item xs={12}>
          <BarPlot data={data} />
        </Grid>
      </Grid>
    </div>
  );
}

export default App;
