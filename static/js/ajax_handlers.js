/**
 * AJAX Handlers for Rate My Society
 * rate, review, and upvote functionality without page reloading
 *  */

$(document).ready(function() {
    setupCSRFToken();
    initializeRatingHandlers();
    initializeReviewHandlers();
    initializeUpvoteHandlers();
});

/**
 * Setup CSRF token for AJAX requests
 */
function setupCSRFToken() {
    var csrftoken = $('[name=csrfmiddlewaretoken]').val();
    if (!csrftoken) {
        csrftoken = getCookie('csrftoken');
    }
    
    if (csrftoken) {
        $.ajaxSetup({
            beforeSend: function(xhr, settings) {
                if (!(/^http:.*/.test(settings.url) || /^https:.*/.test(settings.url))) {
                    xhr.setRequestHeader("X-CSRFToken", csrftoken);
                    xhr.setRequestHeader("X-Requested-With", "XMLHttpRequest");
                }
            }
        });
    }
}

/**
 * Get CSRF token from cookie
 */
function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

/**
 * Initialize rating form handlers
 */
function initializeRatingHandlers() {
    $(document).on('submit', '.rating-form', function(e) {
        e.preventDefault();
        
        var $form = $(this);
        var $submitBtn = $form.find('button[type="submit"]');
        var selectedValue = $form.find('input[name="star"]:checked').val();
        
        if (!selectedValue) {
            return;
        }
        
        submitRatingForm($form);
    });
    
    $(document).on('change', '.rating-form input[type="radio"]', function() {
        var $form = $(this).closest('.rating-form');
        submitRatingForm($form);
    });
}

/**
 * Update average rating display
 */
function updateAverageRatingDisplay(avgRating, totalRatings) {
    var $sidebarRating = $('.detail-rating-avg');
    if ($sidebarRating.length) {
        $sidebarRating.html(`
            <span class="star-display" style="--rating: ${avgRating};"></span>
            <span>${avgRating} / 5</span>
        `);
    }
    
    var $h3 = $('h3').filter(function() {
        return $(this).text().trim() === 'Average Rating';
    });
    
    if ($h3.length) {
        var $p = $h3.next('p');
        if ($p.length) {
            var starsHtml = '';
            for (var i = 1; i <= 5; i++) {
                if (i <= Math.round(avgRating)) {
                    starsHtml += '<i class="fa fa-star"></i>';
                } else {
                    starsHtml += '<i class="fa fa-star-o"></i>';
                }
            }
            $p.html(starsHtml + '<br>(' + avgRating + ' / 5) - ' + totalRatings + ' rating' + (totalRatings !== 1 ? 's' : ''));
        }
    }
}

/**
 * Submit rating form via AJAX
 */
function submitRatingForm($form) {
    var $submitBtn = $form.find('button[type="submit"]');
    var selectedValue = $form.find('input[name="star"]:checked').val();
    
    if (!selectedValue) {
        return;
    }
    
    $submitBtn.prop('disabled', true);
    var originalText = $submitBtn.text();
    $submitBtn.text('Saving...');
    
    $.ajax({
        url: $form.attr('action'),
        type: 'POST',
        data: $form.serialize(),
        dataType: 'json',
        success: function(response) {
            if (response.success) {
                if (response.avg_rating !== undefined) {
                    updateAverageRatingDisplay(response.avg_rating, response.total_ratings);
                }
            }
        },
        error: function(xhr, status, error) {
            // Silent error handling
        },
        complete: function() {
            $submitBtn.prop('disabled', false).text(originalText);
        }
    });
}

/**
 * Initialize review form handlers
 */
function initializeReviewHandlers() {
    $(document).on('submit', '.review-form', function(e) {
        e.preventDefault();
        
        var $form = $(this);
        var $textarea = $form.find('textarea');
        var comment = $textarea.val().trim();
        
        if (!comment) {
            $textarea.focus();
            return;
        }
        
        var $submitBtn = $form.find('button[type="submit"]');
        $submitBtn.prop('disabled', true);
        var originalText = $submitBtn.text();
        $submitBtn.text('Posting...');
        
        $.ajax({
            url: $form.attr('action'),
            type: 'POST',
            data: $form.serialize(),
            dataType: 'json',
            success: function(response) {
                if (response.success) {
                    addReviewToUI(response.review);
                    
                    if (response.avg_rating !== undefined && response.total_ratings !== undefined) {
                        updateAverageRatingDisplay(response.avg_rating, response.total_ratings);
                    }
                    
                    $form[0].reset();
                    $textarea.focus();
                    $submitBtn.prop('disabled', true).text('You have already posted a review');
                    $textarea.prop('disabled', true);
                } else {
                    $submitBtn.prop('disabled', false).text(originalText);
                }
            },
            error: function(xhr) {
                $submitBtn.prop('disabled', false).text(originalText);
            }
        });
    });
}

/**
 * Initialize upvote form handlers
 */
function initializeUpvoteHandlers() {
    $(document).on('submit', '.upvote-form', function(e) {
        e.preventDefault();
        
        var $form = $(this);
        var $submitBtn = $form.find('button[type="submit"]');
        
        $submitBtn.prop('disabled', true);
        var originalText = $submitBtn.text();
        $submitBtn.text('Loading...');
        
        $.ajax({
            url: $form.attr('action'),
            type: 'POST',
            data: $form.serialize(),
            dataType: 'json',
            success: function(response) {
                if (response.success) {
                    $submitBtn.text('👍 ' + response.total_upvotes);
                }
            },
            error: function(xhr) {
                $submitBtn.text(originalText);
            },
            complete: function() {
                $submitBtn.prop('disabled', false);
            }
        });
    });
}

/**
 * Add new review to the UI
 */
function addReviewToUI(reviewData) {
    var reviewHTML = `
        <div class="review-card">
            <div class="review-top">
                <strong class="review-user">${escapeHtml(reviewData.username)}</strong>
                <small class="review-date">${reviewData.created_at}</small>
            </div>
            <p class="review-text">${escapeHtml(reviewData.comment)}</p>
            <div class="review-actions">
                <a href="/rms/reviews/${reviewData.id}/edit/" class="btn">Edit</a>
                <a href="/rms/reviews/${reviewData.id}/delete/" class="btn">Delete</a>
            </div>
            <form method="post" action="/rms/reviews/${reviewData.id}/upvote/" class="upvote-form">
                <input type="hidden" name="csrfmiddlewaretoken" value="${getCookie('csrftoken')}">
                <button type="submit" class="upvote-btn">
                    👍 ${reviewData.upvotes}
                </button>
            </form>
        </div>
    `;
    
    var $reviewsList = $('.reviews-list');
    if ($reviewsList.length) {
        $reviewsList.prepend(reviewHTML);
    }
}


/**
 * Escape HTML to prevent XSS
 */
function escapeHtml(text) {
    var map = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#039;'
    };
    return text.replace(/[&<>"']/g, function(m) { return map[m]; });
}

