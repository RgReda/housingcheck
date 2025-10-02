import { useEffect, useRef } from "react";

interface Props {
  symbol: string;
  theme?: "dark" | "light";
}

const TradingViewWidget: React.FC<Props> = ({ symbol, theme = "light" }) => {
  const container = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!container.current) return;
    container.current.innerHTML = "";

    const script = document.createElement("script");
    script.src = "https://s3.tradingview.com/tv.js";
    script.async = true;
    script.onload = () => {
      // @ts-expect-error: TradingView global chargé dynamiquement
      new TradingView.widget({
        autosize: true,
        symbol,
        interval: "D",
        timezone: "Africa/Casablanca",
        theme,
        style: "1",
        locale: "fr",
        studies: [],
        container_id: container.current?.id,
      });
    };
    container.current.appendChild(script);
  }, [symbol, theme]);

  return <div id={`tv-${symbol.replace(/[:]/g, "-")}`} ref={container} className="h-96 w-full" />;
};

export default TradingViewWidget;
