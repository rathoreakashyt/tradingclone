/**
 * app.js - Main JavaScript file for Broker Platform
 */

// Wait for the DOM to be fully loaded
document.addEventListener('DOMContentLoaded', function() {
    // Mobile menu toggle
    const mobileMenuButton = document.getElementById('mobileMenuButton');
    const mobileMenu = document.getElementById('mobileMenu');
    
    if (mobileMenuButton && mobileMenu) {
        mobileMenuButton.addEventListener('click', function() {
            mobileMenu.classList.toggle('hidden');
        });
    }
    
    // Auto-hide flash messages after 5 seconds
    const flashMessages = document.querySelectorAll('.alert');
    flashMessages.forEach(function(message) {
        setTimeout(function() {
            message.style.opacity = '0';
            setTimeout(function() {
                message.style.display = 'none';
            }, 500);
        }, 5000);
    });
    
    // Form validation enhancer
    const forms = document.querySelectorAll('form');
    forms.forEach(function(form) {
        const requiredInputs = form.querySelectorAll('[required]');
        
        requiredInputs.forEach(function(input) {
            input.addEventListener('blur', function() {
                if (!this.value.trim()) {
                    this.classList.add('border-red-500');
                    
                    // Create error message if it doesn't exist
                    let errorSpan = this.parentNode.querySelector('.error-message');
                    if (!errorSpan) {
                        errorSpan = document.createElement('span');
                        errorSpan.className = 'text-red-600 text-sm error-message';
                        errorSpan.textContent = 'This field is required';
                        this.parentNode.appendChild(errorSpan);
                    }
                } else {
                    this.classList.remove('border-red-500');
                    
                    // Remove error message if it exists
                    const errorSpan = this.parentNode.querySelector('.error-message');
                    if (errorSpan) {
                        errorSpan.remove();
                    }
                }
            });
        });
        
        form.addEventListener('submit', function(event) {
            let isValid = true;
            
            requiredInputs.forEach(function(input) {
                if (!input.value.trim()) {
                    input.classList.add('border-red-500');
                    isValid = false;
                    
                    // Create error message if it doesn't exist
                    let errorSpan = input.parentNode.querySelector('.error-message');
                    if (!errorSpan) {
                        errorSpan = document.createElement('span');
                        errorSpan.className = 'text-red-600 text-sm error-message';
                        errorSpan.textContent = 'This field is required';
                        input.parentNode.appendChild(errorSpan);
                    }
                }
            });
            
            if (!isValid) {
                event.preventDefault();
            }
        });
    });
    
    // Investment amount calculator
    const amountInputs = document.querySelectorAll('.investment-amount');
    
    amountInputs.forEach(function(input) {
        const minInvestment = parseFloat(input.getAttribute('min') || 0);
        const maxInvestment = parseFloat(input.getAttribute('max') || Infinity);
        const roiPercentage = parseFloat(input.getAttribute('data-roi') || 0);
        const durationDays = parseFloat(input.getAttribute('data-duration') || 0);
        const resultElement = document.getElementById(input.getAttribute('data-result'));
        
        if (resultElement) {
            input.addEventListener('input', function() {
                const amount = parseFloat(this.value) || 0;
                
                if (amount < minInvestment) {
                    resultElement.innerHTML = `<span class="text-red-600">Minimum investment amount is $${minInvestment.toLocaleString()}</span>`;
                } else if (maxInvestment !== Infinity && amount > maxInvestment) {
                    resultElement.innerHTML = `<span class="text-red-600">Maximum investment amount is $${maxInvestment.toLocaleString()}</span>`;
                } else {
                    const expectedReturn = amount * (roiPercentage / 100) * (durationDays / 365);
                    const totalReturn = amount + expectedReturn;
                    
                    resultElement.innerHTML = `
                        <div class="mt-2">
                            <div class="flex justify-between mb-1">
                                <span>Expected Profit:</span>
                                <span class="font-bold text-green-600">$${expectedReturn.toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2})}</span>
                            </div>
                            <div class="flex justify-between">
                                <span>Total Return:</span>
                                <span class="font-bold">$${totalReturn.toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2})}</span>
                            </div>
                        </div>
                    `;
                }
            });
        }
    });
    
    // Password strength meter
    const passwordInputs = document.querySelectorAll('input[type="password"]');
    
    passwordInputs.forEach(function(input) {
        if (input.id === 'password' || input.name === 'password') {
            const strengthMeter = document.createElement('div');
            strengthMeter.className = 'w-full h-2 mt-1 rounded-full bg-gray-200';
            
            const strengthBar = document.createElement('div');
            strengthBar.className = 'h-full rounded-full transition-all duration-300';
            strengthBar.style.width = '0%';
            
            const strengthText = document.createElement('div');
            strengthText.className = 'text-xs mt-1';
            
            strengthMeter.appendChild(strengthBar);
            input.parentNode.appendChild(strengthMeter);
            input.parentNode.appendChild(strengthText);
            
            input.addEventListener('input', function() {
                const password = this.value;
                let strength = 0;
                let strengthLabel = '';
                
                if (password.length >= 8) strength += 25;
                if (password.match(/[a-z]/) && password.match(/[A-Z]/)) strength += 25;
                if (password.match(/\d/)) strength += 25;
                if (password.match(/[^a-zA-Z\d]/)) strength += 25;
                
                if (strength === 0) {
                    strengthBar.style.width = '0%';
                    strengthBar.className = 'h-full rounded-full transition-all duration-300';
                    strengthText.textContent = '';
                } else if (strength <= 25) {
                    strengthBar.style.width = '25%';
                    strengthBar.className = 'h-full rounded-full transition-all duration-300 bg-red-500';
                    strengthText.textContent = 'Weak password';
                    strengthText.className = 'text-xs mt-1 text-red-500';
                } else if (strength <= 50) {
                    strengthBar.style.width = '50%';
                    strengthBar.className = 'h-full rounded-full transition-all duration-300 bg-orange-500';
                    strengthText.textContent = 'Fair password';
                    strengthText.className = 'text-xs mt-1 text-orange-500';
                } else if (strength <= 75) {
                    strengthBar.style.width = '75%';
                    strengthBar.className = 'h-full rounded-full transition-all duration-300 bg-yellow-500';
                    strengthText.textContent = 'Good password';
                    strengthText.className = 'text-xs mt-1 text-yellow-600';
                } else {
                    strengthBar.style.width = '100%';
                    strengthBar.className = 'h-full rounded-full transition-all duration-300 bg-green-500';
                    strengthText.textContent = 'Strong password';
                    strengthText.className = 'text-xs mt-1 text-green-600';
                }
            });
        }
    });
});