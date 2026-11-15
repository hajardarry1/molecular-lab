
const API_URL =
  location.hostname === "localhost" || location.hostname === "127.0.0.1"
    ? "http://127.0.0.1:8000"
    : "";

// Démonstration locale uniquement.
// Ne pas conserver ces identifiants dans un site public.
const DEMO_USER = "hajar";
const DEMO_PASSWORD = "hajar1";

const login = document.getElementById("login");
const application = document.getElementById("application");

document.getElementById("loginForm").addEventListener("submit", (e) => {
  e.preventDefault();

  const username = document.getElementById("username").value;
  const password = document.getElementById("password").value;

  if (username === DEMO_USER && password === DEMO_PASSWORD) {
    login.classList.add("hidden");
    application.classList.remove("hidden");
    document.getElementById("loginError").textContent = "";
  } else {
    document.getElementById("loginError").textContent =
      "Incorrect username or password.";
  }
});

document.getElementById("logout").addEventListener("click", () => {
  application.classList.add("hidden");
  login.classList.remove("hidden");
});

const form = document.getElementById("predictionForm");

form.addEventListener("submit", async (e) => {
  e.preventDefault();

  const molecule = document.getElementById("molecule").value.trim();
  const pressure = Number(document.getElementById("pressure").value);
  const unit = document.getElementById("unit").value;
  const status = document.getElementById("status");

  status.textContent = "Calculating molecular properties...";

  try {
    const response = await fetch(`${API_URL}/predict`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ molecule, pressure, unit })
    });

    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.detail || "Calculation failed.");
    }

    document.getElementById("resultName").textContent = data.molecule;
    document.getElementById("resultFormula").textContent = data.formula;
    document.getElementById("resultCAS").textContent = data.cas;

    document.getElementById("resultKelvin").textContent =
      data.tb_kelvin.toFixed(2) + " K";

    document.getElementById("resultCelsius").textContent =
      data.tb_celsius.toFixed(2) + " °C";

    document.getElementById("resultMethod").textContent = data.method;
    document.getElementById("resultSource").textContent =
      "Normal boiling point source: " + data.source;

    status.textContent = "Calculation completed successfully.";

    await displayMolecule(molecule);

    document.getElementById("results").scrollIntoView({
      behavior: "smooth"
    });

  } catch (error) {
    status.textContent = "Error: " + error.message;
  }
});

async function displayMolecule(name) {
  const info = document.getElementById("moleculeInfo");
  const container = document.getElementById("viewer3d");

  info.textContent = "Searching for 3D molecular structure...";

  try {
    const url =
      "https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/" +
      encodeURIComponent(name) +
      "/SDF?record_type=3d";

    const response = await fetch(url);

    if (!response.ok) {
      throw new Error("3D structure not available.");
    }

    const sdf = await response.text();

    if (!sdf.includes("$$$$")) {
      throw new Error("Invalid molecular structure.");
    }

    container.innerHTML = "";

    const viewer = $3Dmol.createViewer(container, {
      backgroundColor: "#F8F0E8"
    });

    viewer.addModel(sdf, "sdf");

    viewer.setStyle({}, {
      stick: { radius: 0.18 },
      sphere: { scale: 0.27 }
    });

    viewer.zoomTo();
    viewer.zoom(0.85);
    viewer.render();
    viewer.spin("y", 0.5);

    info.textContent =
      "3D structure loaded. Use your mouse to rotate and zoom.";

  } catch (error) {
    container.innerHTML = `
      <div class="viewer-placeholder">
        <span>⌬</span>
        <p>3D structure unavailable</p>
        <small>${error.message}</small>
      </div>
    `;

    info.textContent = "Try another molecule or check its 3D availability.";
  }
}
