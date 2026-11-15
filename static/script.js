
let isSearching = false;

console.log("Job Skill Matcher JavaScript loaded!");

// Find the button and results container
const findJobsButton = document.getElementById("findjobs");
const resultsContainer = document.getElementById("results");

// Check whether HTML elements exist
if (!findJobsButton || !resultsContainer) {
    console.error("Find Jobs button or results section not found!");
} else {

    // Button click event
    findJobsButton.addEventListener("click", async function (event) {

        event.preventDefault();

        console.log("Find Jobs button clicked!");

        // Prevent multiple requests
        if (isSearching) {
            console.log("A search is already running.");
            return;
        }

        // Get user inputs
        const skillsInput = document.getElementById("skills").value;
        const roleInput = document.getElementById("role").value;

        // Convert comma-separated skills into an array
        const skills = skillsInput
            .split(",")
            .map(skill => skill.trim().toLowerCase())
            .filter(skill => skill !== "");

        const role = roleInput.trim();

        console.log("User Skills:", skills);
        console.log("Desired Role:", role);

        // Validate inputs
        if (skills.length === 0 || role === "") {
            resultsContainer.style.display = "block";
            resultsContainer.innerHTML = `
                <p>Please enter your skills and desired job role.</p>
            `;
            return;
        }

        // Start searching
        isSearching = true;
        findJobsButton.disabled = true;

        resultsContainer.style.display = "block";
        resultsContainer.innerHTML = `
            <p>Searching for matching jobs...</p>
        `;

        try {

            console.log("Sending request to Flask...");

            // Send data to Flask
            const response = await fetch("/match", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    skills: skills,
                    role: role
                })
            });

            console.log("Flask response status:", response.status);

            // Receive response
            const data = await response.json();

            console.log("FULL RESPONSE:");
            console.log(JSON.stringify(data, null, 2));

            console.log("RESULTS:", data.results);
            console.log("NUMBER OF JOBS:", data.results?.length);

            // Handle errors
            if (!response.ok) {
                throw new Error(data.error || "Something went wrong.");
            }

            // Display results
            displayResults(data);

        } catch (error) {

            console.error("Error:", error);

            resultsContainer.innerHTML = `
                <p class="error">
                    Error: ${escapeHTML(error.message)}
                </p>
            `;

        } finally {

            // Always enable button after request finishes
            isSearching = false;
            findJobsButton.disabled = false;

            console.log("Search completed.");

        }

    });

}


// Function to display matching jobs
function displayResults(data) {

    let html = "";

    html += `
        <h2>Your Matching Results</h2>

        <p>
            <strong>Desired Role:</strong>
            ${escapeHTML(data.desired_role)}
        </p>

        <p>
            <strong>Total Jobs Found:</strong>
            ${data.total_jobs_found ?? 0}
        </p>

        <p>
            <strong>Relevant Jobs:</strong>
            ${data.relevant_jobs ?? 0}
        </p>
    `;

    if (!data.results || data.results.length === 0) {
        html += `
            <p>No relevant jobs found.
            Try another job role.</p>
        `;

        resultsContainer.innerHTML = html;
        return;
    }

    const formatPercentage = value =>
        value === null || value === undefined ? "N/A" : `${value}%`;

    data.results.forEach(job => {
        const skillSource = job.skill_source;
        const hasSkills =
            skillSource !== "none" &&
            job.skill_score !== null &&
            job.skill_score !== undefined;
        const matchedHTML = hasSkills && job.matched_skills?.length
            ? `<ul>${job.matched_skills.map(skill => `
                    <li>${escapeHTML(skill)}</li>
                `).join("")}</ul>`
            : "<p>No matching skills identified.</p>";
        const missingHTML = hasSkills && job.missing_skills?.length
            ? `<div class="missing-list">${job.missing_skills.map(skill => `
                    <div class="skill-card">
                        <span class="skill-name">${escapeHTML(skill.name)}</span>
                        <p>${escapeHTML(skill.explanation)}</p>
                    </div>
                `).join("")}</div>`
            : "<p>No skills to learn identified.</p>";
        const skillNote = skillSource === "role_typical"
            ? `<p class="skill-note">This posting doesn't list skills, so these are skills typically expected for this role.</p>`
            : "";

        html += `
            <div class="result-card">
                <h3>${escapeHTML(job.title)}</h3>
                <p class="company">
                    ${escapeHTML(job.company)} ·
                    ${escapeHTML(job.location)} ·
                    ${escapeHTML(job.salary)}
                </p>
                <div class="score-container">
                    <div class="score-item">
                        <span class="score-value">${formatPercentage(job.overall_score)}</span>
                        <span class="score-label">Overall Match</span>
                    </div>
                    <div class="score-item">
                        <span class="score-value">${formatPercentage(job.role_score)}</span>
                        <span class="score-label">Role Match</span>
                    </div>
                    <div class="score-item">
                        <span class="score-value">${formatPercentage(job.skill_score)}</span>
                        <span class="score-label">Skill Match</span>
                    </div>
                </div>
                <hr class="section-divider">
                ${skillNote}
                <h4>Skills You Have</h4>
                <div class="matched-text">${matchedHTML}</div>
                <h4>Skills to Learn</h4>
                ${missingHTML}
                ${job.link
                    ? `<a class="job-link" href="${safeJobURL(job.link)}"
                          target="_blank" rel="noopener noreferrer">View Job</a>`
                    : `<p>Job link unavailable.</p>`}
            </div>
        `;
    });

    resultsContainer.innerHTML = `<div class="result-summary">${html}</div>`;

}


// Escape HTML to safely display text from API responses
function escapeHTML(value) {

    return String(value ?? "").replace(/[&<>"']/g, character => ({
        "&": "&amp;",
        "<": "&lt;",
        ">": "&gt;",
        '"': "&quot;",
        "'": "&#39;"
    })[character]);

}


// Allow only safe external job links
function safeJobURL(value) {

    try {

        const url = new URL(value);

        if (url.protocol === "https:" || url.protocol === "http:") {
            return escapeHTML(url.href);
        }

    } catch (error) {

        console.log("Invalid job URL:", value);

    }

    return "#";

}
