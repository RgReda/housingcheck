import { useEffect, useRef } from "react";
import { createChart, IChartApi } from "lightweight-charts";

interface Props {
  data: Array<{ time: string; open: number; high: number; low: number; close: number }>;
}

export default function LineOHLC({ data }: Props) {
  const containerRef = useRef<HTMLDivElement>(null);
  const chartRef = useRef<IChartApi | null>(null);

  useEffect(() => {
    if (!containerRef.current) return;
    chartRef.current?.remove();
    chartRef.current = createChart(containerRef.current, {
      width: containerRef.current.clientWidth,
      height: 380,
      layout: {
        background: { color: "transparent" },
        textColor: "#0f172a"
      }
    });
    const series = chartRef.current.addCandlestickSeries();
    series.setData(data);
    const handleResize = () => {
      if (containerRef.current && chartRef.current) {
        chartRef.current.applyOptions({ width: containerRef.current.clientWidth });
      }
    };
    window.addEventListener("resize", handleResize);
    return () => {
      window.removeEventListener("resize", handleResize);
      chartRef.current?.remove();
    };
  }, [data]);

  return <div ref={containerRef} className="w-full" />;
}
