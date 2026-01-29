// Pricing Ops UI logic

document.addEventListener("DOMContentLoaded", () => {

  // ----------------------------------
  // Card entrance animation
  // ----------------------------------
  document.querySelectorAll(".card").forEach(card => {
    card.animate(
      [
        { opacity: 0, transform: "translateY(6px)" },
        { opacity: 1, transform: "translateY(0)" }
      ],
      {
        duration: 180,
        easing: "ease-out",
        fill: "forwards"
      }
    );
  });

  // ----------------------------------
  // Price history chart (SKU Explorer)
  // ----------------------------------
  const canvas = document.getElementById("priceChart");
  if (!canvas) return;

  const sku = new URLSearchParams(window.location.search).get("sku");
  if (!sku) return;

  fetch(`http://127.0.0.1:8000/skus/${sku}/history`)
    .then(res => {
      if (!res.ok) throw new Error("Failed to load price history");
      return res.json();
    })
    .then(data => {
      if (!Array.isArray(data) || data.length === 0) return;

      new Chart(canvas, {
        type: "line",
        data: {
          labels: data.map(d => d.date),
          datasets: [{
            label: "Final Price",
            data: data.map(d => d.price),
            borderColor: "#1a73e8",
            backgroundColor: "rgba(26,115,232,.12)",
            tension: 0.3,
            fill: true,
            pointRadius: 2,
            pointHoverRadius: 4
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: { display: false },
            tooltip: {
              intersect: false,
              mode: "index"
            }
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
    })
    .catch(err => {
      console.warn("Price history chart not rendered:", err.message);
    });

});
