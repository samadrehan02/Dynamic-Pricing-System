document.querySelectorAll(".card").forEach(card => {
  card.animate(
    [
      { opacity: 0, transform: "translateY(6px)" },
      { opacity: 1, transform: "translateY(0)" }
    ],
    { duration: 200, easing: "ease-out" }
  );
});
const chartEl = document.getElementById("priceChart");

if (chartEl) {
  const sku = new URLSearchParams(window.location.search).get("sku");

  fetch(`http://127.0.0.1:8000/skus/${sku}/history`)
    .then(res => res.json())
    .then(data => {
      new Chart(chartEl, {
        type: "line",
        data: {
          labels: data.map(d => d.date),
          datasets: [{
            label: "Final Price",
            data: data.map(d => d.price),
            borderColor: "#1a73e8",
            backgroundColor: "rgba(26,115,232,.1)",
            tension: 0.25,
            fill: true,
          }]
        },
        options: {
          plugins: {
            legend: { display: false }
          },
          scales: {
            x: {
              grid: { display: false }
            },
            y: {
              grid: { color: "#e5e7eb" }
            }
          }
        }
      });
    });
}
