// LinkedIn Clone JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Auto-resize textareas
    const textareas = document.querySelectorAll('textarea');
    textareas.forEach(textarea => {
        textarea.addEventListener('input', function() {
            this.style.height = 'auto';
            this.style.height = this.scrollHeight + 'px';
        });
    });

    // Form validation
    const forms = document.querySelectorAll('.needs-validation');
    forms.forEach(form => {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        });
    });

    // Search functionality
    const searchForm = document.querySelector('form[action="/search"]');
    if (searchForm) {
        const searchInput = searchForm.querySelector('input[name="q"]');
        if (searchInput) {
            searchInput.addEventListener('keyup', function(e) {
                if (e.key === 'Enter') {
                    searchForm.submit();
                }
            });
        }
    }

    // Post creation
    const postForm = document.querySelector('form[action="/posts/create"]');
    if (postForm) {
        const postButton = postForm.querySelector('button[type="submit"]');
        const postTextarea = postForm.querySelector('textarea[name="content"]');
        
        if (postTextarea && postButton) {
            // Enable/disable post button based on content
            postTextarea.addEventListener('input', function() {
                postButton.disabled = this.value.trim().length === 0;
            });
            
            // Initial state
            postButton.disabled = postTextarea.value.trim().length === 0;
        }
    }

    // Connection requests
    const connectionForms = document.querySelectorAll('form[action*="/connections/send/"]');
    connectionForms.forEach(form => {
        form.addEventListener('submit', function(e) {
            const button = form.querySelector('button[type="submit"]');
            if (button) {
                button.disabled = true;
                button.innerHTML = '<i class="bi bi-clock"></i> Sending...';
            }
        });
    });

    // Messaging - conversation selection
    const conversationItems = document.querySelectorAll('.conversation-item');
    conversationItems.forEach(item => {
        item.addEventListener('click', function() {
            // Remove active class from all items
            conversationItems.forEach(i => i.classList.remove('active'));
            // Add active class to clicked item
            this.classList.add('active');
        });
    });

    // Messaging - send message
    const messageInput = document.querySelector('input[placeholder="Type a message..."]');
    const sendButton = document.querySelector('.btn[type="button"] i.bi-send');
    
    if (messageInput && sendButton) {
        messageInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter' && this.value.trim()) {
                sendMessage(this.value.trim());
                this.value = '';
            }
        });
        
        sendButton.parentElement.addEventListener('click', function() {
            if (messageInput.value.trim()) {
                sendMessage(messageInput.value.trim());
                messageInput.value = '';
            }
        });
    }

    // Smooth scrolling for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });

    // Image lazy loading
    const images = document.querySelectorAll('img[data-src]');
    const imageObserver = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const img = entry.target;
                img.src = img.dataset.src;
                img.classList.remove('lazy');
                imageObserver.unobserve(img);
            }
        });
    });

    images.forEach(img => imageObserver.observe(img));
});

// Utility functions
function sendMessage(message) {
    // This would typically send the message to the server
    console.log('Sending message:', message);
    
    // For demo purposes, add the message to the chat
    const messagesContainer = document.querySelector('.overflow-auto');
    if (messagesContainer) {
        const messageElement = document.createElement('div');
        messageElement.className = 'd-flex justify-content-end mb-3';
        messageElement.innerHTML = `
            <div class="text-end">
                <div class="bg-primary text-white rounded p-2 mb-1">
                    <p class="mb-0">${escapeHtml(message)}</p>
                </div>
                <small class="text-muted">Just now</small>
            </div>
        `;
        messagesContainer.appendChild(messageElement);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }
}

function escapeHtml(text) {
    const map = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#039;'
    };
    return text.replace(/[&<>"']/g, function(m) { return map[m]; });
}

function showNotification(message, type = 'info') {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
    notification.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
    notification.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.body.appendChild(notification);
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        if (notification.parentNode) {
            notification.remove();
        }
    }, 5000);
}

// Error handling
window.addEventListener('error', function(e) {
    console.error('JavaScript error:', e.error);
    // You could send this to a logging service
});

// Performance monitoring
window.addEventListener('load', function() {
    // Log page load time
    const loadTime = performance.timing.loadEventEnd - performance.timing.navigationStart;
    console.log('Page load time:', loadTime + 'ms');
});