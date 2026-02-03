const form = document.getElementById("profile-form");
const resultsList = document.getElementById("results-list");
const resultsSection = document.getElementById("results");

const formatCurrency = (value) =>
  new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    maximumFractionDigits: 0,
  }).format(value);

const renderResults = (recommendations) => {
  resultsList.innerHTML = "";
  if (!recommendations.length) {
    resultsList.innerHTML = "<p class='muted'>No scholarships found.</p>";
    return;
  }

  recommendations.slice(0, 10).forEach((item) => {
    const card = document.createElement("div");
    card.className = "result-card";

    const eligibilityClass = item.eligible ? "" : "ineligible";
    const eligibilityText = item.eligible ? "Eligible" : "Not eligible";

    card.innerHTML = `
      <div class="result-header">
        <div>
          <h3>${item.name}</h3>
          <p class="muted">${item.provider}</p>
        </div>
        <span class="badge ${eligibilityClass}">${eligibilityText}</span>
      </div>
      <p>${item.description}</p>
      <div class="details">
        <div><strong>Match Score:</strong> ${item.match_score}%</div>
        <div><strong>Award:</strong> ${formatCurrency(item.award_amount)}</div>
        <div><strong>Deadline:</strong> ${item.deadline}</div>
        <div><strong>Country:</strong> ${item.country}</div>
        <div><strong>Field:</strong> ${item.field}</div>
        <div><strong>Min GPA:</strong> ${item.min_gpa}</div>
      </div>
      ${
        item.reasons.length
          ? `<div class="muted"><strong>Eligibility Notes:</strong> ${item.reasons.join(", ")}</div>`
          : ""
      }
    `;

    resultsList.appendChild(card);
  });
};

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  const formData = new FormData(form);
  const payload = Object.fromEntries(formData.entries());

  resultsSection.querySelector(".muted")?.remove();
  resultsList.innerHTML = "<p class='muted'>Analyzing profile...</p>";

  try {
    const response = await fetch("/api/recommend", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(payload),
    });

    if (!response.ok) {
      throw new Error("Unable to fetch recommendations.");
    }

    const data = await response.json();
    renderResults(data.recommendations || []);
  } catch (error) {
    resultsList.innerHTML = `<p class='muted'>${error.message}</p>`;
  }
});
