// Authentication
$('#loginForm').on('submit', function(e) {
    e.preventDefault();
    
    const email = $('#email').val();
    const password = $('#password').val();
    
    $.ajax({
        url: '/auth/login',
        method: 'POST',
        contentType: 'application/json',
        data: JSON.stringify({ email, password }),
        success: function(response) {
            $('#successMessage').removeClass('d-none').text('Login successful! Redirecting...');
            $('#errorMessage').addClass('d-none');
            setTimeout(() => {
                window.location.href = '/dashboard';
            }, 1500);
        },
        error: function(xhr) {
            const error = xhr.responseJSON?.error || 'Login failed';
            $('#errorMessage').removeClass('d-none').text(error);
            $('#successMessage').addClass('d-none');
        }
    });
});

function logout() {
    $.ajax({
        url: '/auth/logout',
        method: 'POST',
        success: function() {
            window.location.href = '/';
        }
    });
}

// Dashboard functions
function loadDashboardData() {
    // Load summary stats
    $.get('/api/stats/summary', function(data) {
        if (data.success) {
            $('#stepsCount').text(data.data.dailyStepGoal || '-');
            $('#calories').text(data.data.activeKilocalories || '-');
        }
    });
    
    // Load heart rate data
    $.get('/api/heart-rate', function(data) {
        if (data.success) {
            $('#heartRate').text(data.analysis.average + ' bpm');
            updateHeartRateChart(data.analysis.zones);
        }
    });
    
    // Load sleep data
    $.get('/api/sleep', function(data) {
        if (data.success && data.data) {
            const sleepHours = (data.data.sleepTimeSeconds / 3600).toFixed(1);
            $('#sleep').text(sleepHours + ' hrs');
        }
    });
}

function loadRecentActivities() {
    $.get('/api/activities?limit=5', function(data) {
        if (data.success) {
            const tbody = $('#activitiesTable');
            tbody.empty();
            
            data.data.forEach(activity => {
                const row = `
                    <tr>
                        <td>${new Date(activity.startTimeLocal).toLocaleDateString()}</td>
                        <td>${activity.activityName}</td>
                        <td>${formatDuration(activity.duration)}</td>
                        <td>${(activity.distance / 1000).toFixed(2)} km</td>
                        <td>${activity.calories}</td>
                        <td>
                            <button class="btn btn-sm btn-primary" onclick="viewActivity('${activity.activityId}')">View</button>
                            <button class="btn btn-sm btn-secondary" onclick="downloadActivity('${activity.activityId}')">Download</button>
                        </td>
                    </tr>
                `;
                tbody.append(row);
            });
        }
    });
}

function viewActivity(activityId) {
    $.get(`/api/activity/${activityId}`, function(data) {
        if (data.success) {
            // Display activity details in modal
            console.log(data.data);
        }
    });
}

function downloadActivity(activityId) {
    window.location.href = `/api/activity/${activityId}/download?format=FIT`;
}

function formatDuration(seconds) {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = seconds % 60;
    
    if (hours > 0) {
        return `${hours}h ${minutes}m`;
    } else {
        return `${minutes}m ${secs}s`;
    }
}

// Charts
let hrZonesChart, weeklyChart;

function initializeCharts() {
    // Heart Rate Zones Chart
    const hrCtx = document.getElementById('hrZonesChart')?.getContext('2d');
    if (hrCtx) {
        hrZonesChart = new Chart(hrCtx, {
            type: 'doughnut',
            data: {
                labels: ['Zone 1', 'Zone 2', 'Zone 3', 'Zone 4', 'Zone 5'],
                datasets: [{
                    data: [0, 0, 0, 0, 0],
                    backgroundColor: [
                        '#4CAF50',
                        '#8BC34A',
                        '#FFC107',
                        '#FF9800',
                        '#F44336'
                    ]
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false
            }
        });
    }
    
    // Weekly Activity Chart
    const weeklyCtx = document.getElementById('weeklyChart')?.getContext('2d');
    if (weeklyCtx) {
        weeklyChart = new Chart(weeklyCtx, {
            type: 'bar',
            data: {
                labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
                datasets: [{
                    label: 'Activities',
                    data: [0, 0, 0, 0, 0, 0, 0],
                    backgroundColor: '#2196F3'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });
    }
}

function updateHeartRateChart(zones) {
    if (hrZonesChart && zones) {
        hrZonesChart.data.datasets[0].data = [
            zones.zone1 || 0,
            zones.zone2 || 0,
            zones.zone3 || 0,
            zones.zone4 || 0,
            zones.zone5 || 0
        ];
        hrZonesChart.update();
    }
}

// File upload
$('#uploadForm').on('submit', function(e) {
    e.preventDefault();
    
    const fileInput = document.getElementById('fitFile');
    const file = fileInput.files[0];
    
    if (!file) {
        alert('Please select a file');
        return;
    }
    
    const formData = new FormData();
    formData.append('file', file);
    
    $.ajax({
        url: '/api/upload/fit',
        method: 'POST',
        data: formData,
        processData: false,
        contentType: false,
        success: function(response) {
            console.log('File analyzed:', response);
            alert('File analyzed successfully! Check console for details.');
        },
        error: function(xhr) {
            alert('Error analyzing file: ' + xhr.responseJSON?.error);
        }
    });
});