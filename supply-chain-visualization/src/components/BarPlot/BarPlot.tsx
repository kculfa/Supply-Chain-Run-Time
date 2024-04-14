import React, { useEffect, useRef } from "react";
import * as d3 from "d3";
import { DataPoint } from "../../constants";

const settings = {
  width: 750,
  height: 500,
  margin: { top: 20, right: 20, bottom: 30, left: 40 },
};

const SKUs: string[]  = []
for(let i = 0; i < 10; i++) {
	SKUs.push(`SKU${i}`)
}

export default function BarPlot({ data }: { data: DataPoint[] }) {
  const svgRef = useRef(null);
  useEffect(() => {
    const svg = d3.select(svgRef.current);
    svg.selectAll("*").remove();
    const x = d3
      .scaleBand()
      .domain(SKUs)
      .range([settings.margin.left, settings.width])
      .padding(0.1);

    const y = d3
      .scaleLinear()
      .domain([0, 100])
      .nice()
      .range([settings.height - settings.margin.bottom, settings.margin.top]);

    svg
      .append("g")
      .attr("fill", "steelblue")
      .selectAll("rect")
      .data(data)
      .join("rect")
      .attr("x", (d) => {
        return x(d.SKU) || "";
      })
      .attr("y", (d) => y(d["Discount"]))
      .attr("height", (d) => y(0) - y(d["Discount"]))
      .attr("width", x.bandwidth());

    svg
      .append("g")
      .attr(
        "transform",
        `translate(0,${settings.height - settings.margin.bottom})`
      )
      .call(d3.axisBottom(x));

    svg
      .append("g")
      .attr("transform", `translate(${settings.margin.left},0)`)
      .call(d3.axisLeft(y));
  }, [data]);

  return (
    <svg
      style={{ height: settings.height, width: settings.width }}
      ref={svgRef}
    ></svg>
  );
}
