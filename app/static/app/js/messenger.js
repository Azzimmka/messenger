class Messenger {
    constructor() {
        this.currentContactId = null;
        this.messagesContainer = null;
        this.messageInput = null;
        this.sendButton = null;
        this.refreshInterval = null;
        
        this.init();
    }
    
    init() {
        this.initTheme();
        this.initMessageInput();
        this.initContactSelection();
        this.initAutoRefresh();
        this.initSendMessage();
    }
    
    initTheme() {
        const themeToggle = document.querySelector('.theme-toggle');
        const savedTheme = localStorage.getItem('theme') || 'light';
        
        document.documentElement.setAttribute('data-theme', savedTheme);
        this.updateThemeIcon(savedTheme);
        
        if (themeToggle) {
            themeToggle.addEventListener('click', () => {
                const currentTheme = document.documentElement.getAttribute('data-theme');
                const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
                
                document.documentElement.setAttribute('data-theme', newTheme);
                localStorage.setItem('theme', newTheme);
                this.updateThemeIcon(newTheme);
            });
        }
    }
    
    updateThemeIcon(theme) {
        const themeToggle = document.querySelector('.theme-toggle');
        if (themeToggle) {
            themeToggle.innerHTML = theme === 'dark' ? 
                '<i class="fas fa-sun"></i>' : 
                '<i class="fas fa-moon"></i>';
        }
    }
    
    initMessageInput() {
        this.messageInput = document.querySelector('.message-input');
        this.sendButton = document.querySelector('.send-button');
        
        if (this.messageInput) {
            // Auto-resize textarea
            this.messageInput.addEventListener('input', (e) => {
                e.target.style.height = 'auto';
                e.target.style.height = Math.min(e.target.scrollHeight, 120) + 'px';
                
                // Enable/disable send button
                if (this.sendButton) {
                    this.sendButton.disabled = !e.target.value.trim();
                }
            });
            
            // Send message on Enter (but not Shift+Enter)
            this.messageInput.addEventListener('keydown', (e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    this.sendMessage();
                }
            });
        }
    }
    
    initContactSelection() {
        const contactItems = document.querySelectorAll('.contact-item');
        const urlParams = new URLSearchParams(window.location.search);
        this.currentContactId = urlParams.get('contact_id');
        
        contactItems.forEach(item => {
            const contactId = item.getAttribute('href')?.split('contact_id=')[1];
            
            if (contactId === this.currentContactId) {
                item.classList.add('active');
            }
            
            item.addEventListener('click', (e) => {
                // Remove active class from all contacts
                contactItems.forEach(c => c.classList.remove('active'));
                // Add active class to clicked contact
                item.classList.add('active');
            });
        });
    }
    
    initAutoRefresh() {
        if (this.currentContactId) {
            this.messagesContainer = document.querySelector('.messages-container');
            this.startMessageRefresh();
        }
    }
    
    startMessageRefresh() {
        // Refresh messages every 3 seconds
        this.refreshInterval = setInterval(() => {
            this.refreshMessages();
        }, 3000);
    }
    
    stopMessageRefresh() {
        if (this.refreshInterval) {
            clearInterval(this.refreshInterval);
            this.refreshInterval = null;
        }
    }
    
    async refreshMessages() {
        if (!this.currentContactId || !this.messagesContainer) return;
        
        try {
            const response = await fetch(`/api/messages/?contact_id=${this.currentContactId}`);
            if (!response.ok) throw new Error('Failed to fetch messages');
            
            const data = await response.json();
            this.updateMessagesDisplay(data.messages);
        } catch (error) {
            console.error('Error refreshing messages:', error);
        }
    }
    
    updateMessagesDisplay(messages) {
        const currentMessages = this.messagesContainer.querySelectorAll('.message');
        
        // Only update if message count has changed
        if (messages.length !== currentMessages.length) {
            this.messagesContainer.innerHTML = '';
            
            messages.forEach(msg => {
                const messageEl = this.createMessageElement(msg);
                this.messagesContainer.appendChild(messageEl);
            });
            
            this.scrollToBottom();
        }
    }
    
    createMessageElement(message) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${message.is_mine ? 'sent' : 'received'}`;
        
        const bubbleDiv = document.createElement('div');
        bubbleDiv.className = 'message-bubble';
        
        const contentP = document.createElement('p');
        contentP.className = 'message-content';
        contentP.textContent = message.content;
        
        const timeDiv = document.createElement('div');
        timeDiv.className = 'message-time';
        timeDiv.innerHTML = `
            ${message.timestamp}
            ${message.is_mine ? `<span class="message-status">✓</span>` : ''}
        `;
        
        bubbleDiv.appendChild(contentP);
        bubbleDiv.appendChild(timeDiv);
        messageDiv.appendChild(bubbleDiv);
        
        return messageDiv;
    }
    
    initSendMessage() {
        if (this.sendButton) {
            this.sendButton.addEventListener('click', (e) => {
                e.preventDefault();
                this.sendMessage();
            });
        }
        
        // Also handle form submission
        const messageForm = document.querySelector('.message-input-form');
        if (messageForm) {
            messageForm.addEventListener('submit', (e) => {
                e.preventDefault();
                this.sendMessage();
            });
        }
    }
    
    sendMessage() {
        if (!this.messageInput || !this.messageInput.value.trim()) return;
        
        const content = this.messageInput.value.trim();
        this.messageInput.value = '';
        this.messageInput.style.height = 'auto';
        
        if (this.sendButton) {
            this.sendButton.disabled = true;
        }
        
        // Create form data
        const formData = new FormData();
        formData.append('content', content);
        formData.append('csrfmiddlewaretoken', this.getCSRFToken());
        
        // Send message via AJAX
        fetch(window.location.href, {
            method: 'POST',
            body: formData,
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
        .then(response => {
            if (response.ok) {
                // Immediately refresh messages to show the new message
                this.refreshMessages();
            } else {
                console.error('Failed to send message');
            }
        })
        .catch(error => {
            console.error('Error sending message:', error);
        })
        .finally(() => {
            if (this.sendButton) {
                this.sendButton.disabled = false;
            }
        });
    }
    
    getCSRFToken() {
        const cookies = document.cookie.split(';');
        for (let cookie of cookies) {
            const [name, value] = cookie.trim().split('=');
            if (name === 'csrftoken') {
                return value;
            }
        }
        
        // Fallback to meta tag or hidden input
        const metaToken = document.querySelector('meta[name="csrf-token"]');
        if (metaToken) {
            return metaToken.getAttribute('content');
        }
        
        const hiddenToken = document.querySelector('[name="csrfmiddlewaretoken"]');
        if (hiddenToken) {
            return hiddenToken.value;
        }
        
        return '';
    }
    
    scrollToBottom() {
        if (this.messagesContainer) {
            this.messagesContainer.scrollTop = this.messagesContainer.scrollHeight;
        }
    }
    
    // Public method to clean up when leaving the page
    destroy() {
        this.stopMessageRefresh();
    }
}

// Utility functions
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `alert alert-${type}`;
    notification.textContent = message;
    
    const container = document.querySelector('.chat-main') || document.body;
    container.insertBefore(notification, container.firstChild);
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        notification.remove();
    }, 5000);
}

function formatTime(date) {
    return date.toLocaleTimeString('en-US', {
        hour: '2-digit',
        minute: '2-digit',
        hour12: false
    });
}

function copyToClipboard(text) {
    if (navigator.clipboard) {
        navigator.clipboard.writeText(text);
    } else {
        const textArea = document.createElement('textarea');
        textArea.value = text;
        document.body.appendChild(textArea);
        textArea.select();
        document.execCommand('copy');
        document.body.removeChild(textArea);
    }
    
    showNotification('Copied to clipboard!', 'success');
}

// Initialize the messenger when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.messenger = new Messenger();
});

// Clean up when leaving the page
window.addEventListener('beforeunload', () => {
    if (window.messenger) {
        window.messenger.destroy();
    }
});

// Handle responsive sidebar toggle
function toggleSidebar() {
    const sidebar = document.querySelector('.chat-sidebar');
    if (sidebar) {
        sidebar.classList.toggle('open');
    }
}

// Add click outside to close sidebar on mobile
document.addEventListener('click', (e) => {
    const sidebar = document.querySelector('.chat-sidebar');
    const toggleButton = document.querySelector('.sidebar-toggle');
    
    if (sidebar && window.innerWidth <= 768) {
        if (!sidebar.contains(e.target) && !toggleButton?.contains(e.target)) {
            sidebar.classList.remove('open');
        }
    }
});

// Handle window resize
window.addEventListener('resize', () => {
    const sidebar = document.querySelector('.chat-sidebar');
    if (sidebar && window.innerWidth > 768) {
        sidebar.classList.remove('open');
    }
});

// Emoji picker functionality (simple)
function insertEmoji(emoji) {
    const messageInput = document.querySelector('.message-input');
    if (messageInput) {
        const start = messageInput.selectionStart;
        const end = messageInput.selectionEnd;
        const text = messageInput.value;
        
        messageInput.value = text.substring(0, start) + emoji + text.substring(end);
        messageInput.focus();
        messageInput.setSelectionRange(start + emoji.length, start + emoji.length);
        
        // Trigger input event to update send button state
        messageInput.dispatchEvent(new Event('input'));
    }
}

// Popular emojis for quick access
const popularEmojis = ['😀', '😂', '🥰', '😍', '🤔', '👍', '👎', '❤️', '🔥', '💯'];

// Add emoji picker to page if needed
function createEmojiPicker() {
    const picker = document.createElement('div');
    picker.className = 'emoji-picker';
    picker.innerHTML = popularEmojis.map(emoji => 
        `<button type="button" onclick="insertEmoji('${emoji}')">${emoji}</button>`
    ).join('');
    
    return picker;
}
