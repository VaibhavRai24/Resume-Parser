// Global state
let currentResumeData = null;
let currentAtsScore = null;
let currentOutputFile = null;

// Tab switching
document.querySelectorAll('.tab-btn').forEach(btn => {
    btn.addEventListener('click', (e) => {
        const tab = e.target.dataset.tab;
        
        // Update active tab button
        document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
        e.target.classList.add('active');
        
        // Update active content
        document.querySelectorAll('.tab-content').forEach(content => {
            content.classList.remove('active');
        });
        document.getElementById(`${tab}-tab`).classList.add('active');
    });
});

// File upload handling
const fileInput = document.getElementById('file-input');
const uploadBtn = document.getElementById('upload-btn');
const uploadLabel = document.querySelector('.upload-label');

fileInput.addEventListener('change', (e) => {
    if (e.target.files.length > 0) {
        uploadBtn.disabled = false;
        uploadLabel.querySelector('p').textContent = e.target.files[0].name;
    }
});

uploadBtn.addEventListener('click', async () => {
    const file = fileInput.files[0];
    if (!file) return;
    
    await uploadResume(file);
});

// Upload resume
async function uploadResume(file) {
    const formData = new FormData();
    formData.append('file', file);
    
    showLoading(true);
    try {
        const response = await fetch('/api/upload', {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        if (data.error) {
            alert('Error: ' + data.error);
            return;
        }
        
        currentResumeData = data.parsed_data;
        currentAtsScore = data.ats_score;
        currentOutputFile = data.output_file;
        
        updateSteps(2);
        displayResults();
        
    } catch (error) {
        console.error('Error:', error);
        alert('Error uploading resume: ' + error.message);
    } finally {
        showLoading(false);
    }
}

// Manual form submission
document.getElementById('manual-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const experience = [];
    document.querySelectorAll('.form-group').forEach(group => {
        const title = group.querySelector('.exp-title')?.value;
        const company = group.querySelector('.exp-company')?.value;
        const duration = group.querySelector('.exp-duration')?.value;
        const desc = group.querySelector('.exp-desc')?.value;
        
        if (title && company) {
            experience.push({
                title, company, duration, description: desc
            });
        }
    });
    
    const education = [];
    document.querySelectorAll('.form-group').forEach(group => {
        const degree = group.querySelector('.edu-degree')?.value;
        const field = group.querySelector('.edu-field')?.value;
        const institution = group.querySelector('.edu-institution')?.value;
        const year = group.querySelector('.edu-year')?.value;
        
        if (degree && institution) {
            education.push({
                degree, field, institution, year
            });
        }
    });
    
    const skillsText = document.getElementById('skills-input').value;
    const skills = skillsText.split(',').map(s => s.trim()).filter(s => s);
    
    const resumeData = {
        name: document.getElementById('name').value,
        email: document.getElementById('email').value,
        phone: document.getElementById('phone').value,
        summary: document.getElementById('summary').value,
        experience,
        education,
        skills,
        projects: []
    };
    
    await processManualResume(resumeData);
});

// Process manual resume
async function processManualResume(data) {
    showLoading(true);
    try {
        const response = await fetch('/api/process-manual', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        });
        
        const result = await response.json();
        
        if (result.error) {
            alert('Error: ' + result.error);
            return;
        }
        
        currentResumeData = result.parsed_data;
        currentAtsScore = result.ats_score;
        currentOutputFile = result.output_file;
        
        updateSteps(3);
        displayResults();
        
    } catch (error) {
        console.error('Error:', error);
        alert('Error processing resume: ' + error.message);
    } finally {
        showLoading(false);
    }
}

// Enhance resume with AI
async function enhanceResume() {
    showLoading(true);
    try {
        const response = await fetch('/api/enhance', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(currentResumeData)
        });
        
        const data = await response.json();
        
        if (data.error) {
            alert('Error: ' + data.error);
            return;
        }
        
        // Update with enhanced data
        currentResumeData = data.enhanced_data;
        currentAtsScore = data.ats_score;
        
        // Update ATS score display
        updateAtsScore();
        displayPreview();
        
        alert('Resume enhanced successfully!');
        document.getElementById('download-btn').disabled = false;
        
    } catch (error) {
        console.error('Error:', error);
        alert('Error enhancing resume: ' + error.message);
    } finally {
        showLoading(false);
    }
}

// Download resume
async function downloadResume() {
    if (!currentOutputFile) {
        alert('No resume to download');
        return;
    }
    
    try {
        window.location.href = `/api/download/${currentOutputFile.split('/').pop()}`;
    } catch (error) {
        console.error('Error:', error);
        alert('Error downloading resume');
    }
}

// Update steps indicator
function updateSteps(step) {
    for (let i = 1; i <= 4; i++) {
        const stepEl = document.getElementById(`step-${i}`);
        if (i <= step) {
            stepEl.classList.add('active');
        } else {
            stepEl.classList.remove('active');
        }
    }
}

// Display results
function displayResults() {
    document.getElementById('upload-tab').classList.add('hidden');
    document.getElementById('manual-tab').classList.add('hidden');
    document.getElementById('results-section').classList.remove('hidden');
    
    updateAtsScore();
    displayPreview();
}

// Update ATS score display
function updateAtsScore() {
    if (!currentAtsScore) return;
    
    const score = currentAtsScore.score || 0;
    const feedback = currentAtsScore.feedback || 'No feedback';
    const improvements = currentAtsScore.improvements || [];
    
    document.getElementById('score-value').textContent = Math.round(score);
    document.getElementById('score-feedback').textContent = feedback;
    
    const improvementsList = document.getElementById('improvements-list');
    improvementsList.innerHTML = '';
    improvements.forEach(improvement => {
        const li = document.createElement('li');
        li.textContent = improvement;
        improvementsList.appendChild(li);
    });
    
    // Change score circle color based on score
    const scoreCircle = document.querySelector('.score-circle');
    if (score >= 80) {
        scoreCircle.style.borderColor = '#10b981';
        scoreCircle.style.color = '#10b981';
    } else if (score >= 60) {
        scoreCircle.style.borderColor = '#f59e0b';
        scoreCircle.style.color = '#f59e0b';
    } else {
        scoreCircle.style.borderColor = '#ef4444';
        scoreCircle.style.color = '#ef4444';
    }
}

// Display preview
function displayPreview() {
    if (!currentResumeData) return;
    
    const preview = document.getElementById('preview-content');
    let html = '';
    
    // Personal info
    html += `
        <div class="preview-section">
            <h4>${currentResumeData.name || 'Name'}</h4>
            <p>${currentResumeData.email || ''} | ${currentResumeData.phone || ''}</p>
        </div>
    `;
    
    // Summary
    if (currentResumeData.summary) {
        html += `
            <div class="preview-section">
                <h4>Professional Summary</h4>
                <p>${currentResumeData.summary}</p>
            </div>
        `;
    }
    
    // Experience
    if (currentResumeData.experience && currentResumeData.experience.length > 0) {
        html += '<div class="preview-section"><h4>Experience</h4>';
        currentResumeData.experience.forEach(exp => {
            html += `
                <div class="preview-item">
                    <strong>${exp.title}</strong> at <strong>${exp.company}</strong>
                    <p>${exp.duration}</p>
                    <p>${exp.description}</p>
                </div>
            `;
        });
        html += '</div>';
    }
    
    // Education
    if (currentResumeData.education && currentResumeData.education.length > 0) {
        html += '<div class="preview-section"><h4>Education</h4>';
        currentResumeData.education.forEach(edu => {
            html += `
                <div class="preview-item">
                    <strong>${edu.degree} in ${edu.field}</strong>
                    <p>${edu.institution}</p>
                </div>
            `;
        });
        html += '</div>';
    }
    
    // Skills
    if (currentResumeData.skills && currentResumeData.skills.length > 0) {
        html += `
            <div class="preview-section">
                <h4>Skills</h4>
                <p>${currentResumeData.skills.join(', ')}</p>
            </div>
        `;
    }
    
    preview.innerHTML = html;
}

// Show/hide loading
function showLoading(show) {
    const loading = document.getElementById('loading');
    if (show) {
        loading.classList.remove('hidden');
    } else {
        loading.classList.add('hidden');
    }
}

// Add experience (dynamic form)
function addExperience() {
    const container = document.getElementById('experience-container');
    const group = document.createElement('div');
    group.className = 'form-group';
    group.innerHTML = `
        <input type="text" placeholder="Job Title" class="exp-title form-input">
        <input type="text" placeholder="Company" class="exp-company form-input">
        <input type="text" placeholder="Duration" class="exp-duration form-input">
        <textarea placeholder="Description" class="exp-desc form-textarea" rows="3"></textarea>
        <button type="button" class="btn btn-secondary" onclick="this.parentElement.remove()">Remove</button>
    `;
    container.appendChild(group);
}

// Add education (dynamic form)
function addEducation() {
    const container = document.getElementById('education-container');
    const group = document.createElement('div');
    group.className = 'form-group';
    group.innerHTML = `
        <input type="text" placeholder="Degree" class="edu-degree form-input">
        <input type="text" placeholder="Field of Study" class="edu-field form-input">
        <input type="text" placeholder="Institution" class="edu-institution form-input">
        <input type="text" placeholder="Year" class="edu-year form-input">
        <button type="button" class="btn btn-secondary" onclick="this.parentElement.remove()">Remove</button>
    `;
    container.appendChild(group);
}

console.log('AI Resume Builder initialized');
