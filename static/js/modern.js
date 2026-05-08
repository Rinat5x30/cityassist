/**
 * CityAssist Modern UI JavaScript
 * Handles interactions, animations, and form functionality
 */

document.addEventListener('DOMContentLoaded', function () {
    // Initialize all modules
    initNavbar();
    initScrollAnimations();
    initDragDropUpload();
    initFormValidation();
    initGPSButton();
});

/**
 * Mobile Navigation Toggle
 */
function initNavbar() {
    const navbarToggle = document.getElementById('navbarToggle');
    const navbarMenu = document.getElementById('navbarMenu');

    if (navbarToggle && navbarMenu) {
        navbarToggle.addEventListener('click', function () {
            navbarMenu.classList.toggle('active');

            // Animate hamburger to X
            const spans = navbarToggle.querySelectorAll('span');
            navbarMenu.classList.contains('active')
                ? spans.forEach(s => s.style.background = 'var(--color-primary)')
                : spans.forEach(s => s.style.background = '');
        });

        // Close menu on link click
        const navLinks = navbarMenu.querySelectorAll('a');
        navLinks.forEach(link => {
            link.addEventListener('click', () => {
                navbarMenu.classList.remove('active');
            });
        });
    }

    // Navbar scroll effect
    const navbar = document.getElementById('navbar');
    if (navbar) {
        let lastScroll = 0;
        window.addEventListener('scroll', function () {
            const currentScroll = window.pageYOffset;

            if (currentScroll > 50) {
                navbar.style.boxShadow = 'var(--shadow-md)';
            } else {
                navbar.style.boxShadow = 'none';
            }

            lastScroll = currentScroll;
        });
    }
}

/**
 * Scroll Animations (Fade in on scroll)
 */
function initScrollAnimations() {
    const fadeElements = document.querySelectorAll('.fade-in');

    if (fadeElements.length === 0) return;

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('visible');
                observer.unobserve(entry.target);
            }
        });
    }, {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    });

    fadeElements.forEach(el => observer.observe(el));
}

/**
 * Drag & Drop File Upload
 */
function initDragDropUpload() {
    const uploadArea = document.getElementById('uploadArea');
    const uploadInput = document.getElementById('photo');
    const uploadPreview = document.getElementById('uploadPreview');
    const submitBtn = document.getElementById('submitBtn');

    if (!uploadArea || !uploadInput) return;

    // Click to upload
    uploadArea.addEventListener('click', (e) => {
        if (e.target === uploadInput) {
            return;
        }
        uploadInput.click();
    });

    // File selection
    uploadInput.addEventListener('change', handleFileSelect);

    // Drag & drop events
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        uploadArea.addEventListener(eventName, preventDefaults, false);
    });

    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }

    ['dragenter', 'dragover'].forEach(eventName => {
        uploadArea.addEventListener(eventName, () => {
            uploadArea.classList.add('dragover');
        }, false);
    });

    ['dragleave', 'drop'].forEach(eventName => {
        uploadArea.addEventListener(eventName, () => {
            uploadArea.classList.remove('dragover');
        }, false);
    });

    uploadArea.addEventListener('drop', (e) => {
        const files = e.dataTransfer.files;
        if (files.length) {
            uploadInput.files = files;
            handleFileSelect({ target: uploadInput });
        }
    });

    function handleFileSelect(e) {
        const file = e.target.files[0];

        if (!file) return;

        // Validate file type
        if (!file.type.startsWith('image/')) {
            alert('Zəhmət olmasa, şəkil yükləyin');
            return;
        }

        // Show preview
        const reader = new FileReader();
        reader.onload = (e) => {
            uploadPreview.src = e.target.result;
            uploadPreview.classList.add('show');
            uploadArea.classList.add('has-file');

            // Update UI
            const uploadText = uploadArea.querySelector('.upload-text');
            if (uploadText) {
                uploadText.textContent = file.name;
            }

            // Enable submit button
            if (submitBtn) {
                submitBtn.disabled = false;
            }
        };
        reader.readAsDataURL(file);
    }
}

/**
 * Form Validation
 */
function initFormValidation() {
    const form = document.getElementById('reportForm');
    const submitBtn = document.getElementById('submitBtn');

    if (!form || !submitBtn) return;

    // Initially disable submit until image is uploaded
    submitBtn.disabled = true;

    form.addEventListener('submit', function (e) {
        const photo = document.getElementById('photo').files[0];
        const address = document.getElementById('address').value.trim();
        const description = document.getElementById('description').value.trim();

        if (!photo) {
            e.preventDefault();
            showError('Zəhmət olmasa, foto yükləyin');
            return;
        }

        if (!address) {
            e.preventDefault();
            showError('Zəhmət olmasa, ünvan daxil edin');
            document.getElementById('address').focus();
            return;
        }

        if (!description) {
            e.preventDefault();
            showError('Zəhmət olmasa, problemi təsvir edin');
            document.getElementById('description').focus();
            return;
        }

        // Show loading state
        submitBtn.classList.add('loading');
        submitBtn.disabled = true;
    });
}

/**
 * GPS Location Button with Reverse Geocoding
 */
function initGPSButton() {
    const gpsBtn = document.getElementById('gpsBtn');
    const latInput = document.getElementById('latitude');
    const lngInput = document.getElementById('longitude');
    const addressInput = document.getElementById('address');
    const gpsStatus = document.getElementById('gpsStatus');

    if (!gpsBtn) return;

    gpsBtn.addEventListener('click', function () {
        if (!navigator.geolocation) {
            showGPSStatus('Geolocation brauzeriniz tərəfindən dəstəklənmir', 'error');
            return;
        }

        gpsBtn.classList.add('loading');
        showGPSStatus('Məkan müəyyən edilir...', 'info');

        navigator.geolocation.getCurrentPosition(
            async (position) => {
                const lat = position.coords.latitude;
                const lng = position.coords.longitude;

                // Set coordinates in hidden inputs
                latInput.value = lat;
                lngInput.value = lng;

                // Reverse geocoding - convert coordinates to address
                try {
                    showGPSStatus('Ünvan alınır...', 'info');
                    const address = await getAddressFromCoords(lat, lng);

                    if (address && addressInput) {
                        addressInput.value = address;
                        gpsBtn.classList.remove('loading');
                        showGPSStatus(`Koordinatlar: ${lat.toFixed(4)}, ${lng.toFixed(4)}`, 'success');
                    } else {
                        gpsBtn.classList.remove('loading');
                        showGPSStatus(`Koordinatlar: ${lat.toFixed(4)}, ${lng.toFixed(4)}`, 'success');
                    }
                } catch (err) {
                    gpsBtn.classList.remove('loading');
                    showGPSStatus(`Koordinatlar: ${lat.toFixed(4)}, ${lng.toFixed(4)}`, 'success');
                }
            },
            (error) => {
                gpsBtn.classList.remove('loading');
                let message = 'Məkan müəyyən edilə bilmədi';

                switch (error.code) {
                    case error.PERMISSION_DENIED:
                        message = 'Geolokasiyaya giriş qadağandır';
                        break;
                    case error.POSITION_UNAVAILABLE:
                        message = 'Məkan məlumatı əlçatan deyil';
                        break;
                    case error.TIMEOUT:
                        message = 'Gözləmə vaxtı aşıldı';
                        break;
                }

                showGPSStatus(message, 'error');
            },
            { enableHighAccuracy: true, timeout: 10000, maximumAge: 0 }
        );
    });
}

/**
 * Reverse Geocoding - Get address from coordinates using OpenStreetMap Nominatim
 */
async function getAddressFromCoords(lat, lng) {
    try {
        const response = await fetch(
            `https://nominatim.openstreetmap.org/reverse?format=json&lat=${lat}&lon=${lng}&accept-language=az`,
            { headers: { 'User-Agent': 'CityAssist/1.0' } }
        );

        if (!response.ok) {
            throw new Error('Network response was not ok');
        }

        const data = await response.json();

        if (data && data.display_name) {
            // Return formatted address, removing duplicate country name if present at the end
            let address = data.display_name;
            const parts = address.split(', ');

            // Build cleaner address (remove postcode at the beginning if present)
            const cleanParts = parts.filter(part => !/^\d{5,6}$/.test(part.trim()));

            // Limit to reasonable number of parts for cleaner address
            const relevantParts = cleanParts.slice(0, 6);
            return relevantParts.join(', ');
        }

        return null;
    } catch (error) {
        console.error('Reverse geocoding error:', error);
        return null;
    }
}

function showGPSStatus(message, type) {
    const gpsStatus = document.getElementById('gpsStatus');
    if (!gpsStatus) return;

    gpsStatus.textContent = message;
    gpsStatus.className = 'gps-status';

    if (type === 'success') {
        gpsStatus.style.color = 'var(--color-success)';
    } else if (type === 'error') {
        gpsStatus.style.color = 'var(--color-error)';
    } else {
        gpsStatus.style.color = 'var(--color-text-light)';
    }
}

/**
 * Error Messages
 */
function showError(message) {
    // Create toast notification
    const toast = document.createElement('div');
    toast.className = 'alert alert-error';
    toast.style.cssText = `
        position: fixed;
        top: 100px;
        left: 50%;
        transform: translateX(-50%);
        z-index: 9999;
        animation: slideDown 0.3s ease;
    `;
    toast.innerHTML = `
        <i class="fas fa-exclamation-circle"></i>
        ${message}
        <button type="button" class="alert-close" onclick="this.parentElement.remove()">&times;</button>
    `;

    document.body.appendChild(toast);

    // Auto remove after 5 seconds
    setTimeout(() => {
        toast.remove();
    }, 5000);
}
