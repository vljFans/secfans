function setCookie(cookieName, cookieValue) {
    // expirationDays = 180;
    // const d = new Date();
    // d.setTime(d.getTime() + (expirationDays * 24 * 60 * 60 * 1000)); // Calculate expiration date

    // const expires = "expires=" + d.toUTCString();
    // document.cookie = cookieName + "=" + cookieValue + "; " + expires;
    document.cookie = cookieName + "=" + cookieValue + ";";
}

function getCookieValue(cookieName) {
    const name = cookieName + '=';
    const decodedCookie = decodeURIComponent(document.cookie);
    const cookieArray = decodedCookie.split(';');

    for (let i = 0; i < cookieArray.length; i++) {
        let cookie = cookieArray[i].trim();

        if (cookie.indexOf(name) === 0) {
            return cookie.substring(name.length, cookie.length);
        }
    }

    return null; // Return null if the cookie is not found
}

function deleteCookie(cookieName) {
    // Set the cookie's expiration date to a date in the past
    document.cookie = `${cookieName}=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;`;
}

function locationAfterMessageStore(message, message_type = null, redirect_path = null) {
    $.ajax({
        type: "POST",
        url: "/message-store",
        data: ({ message: message, message_type: message_type }),
        success: function (message_response) {
            if (redirect_path != null) {
                window.location.href = redirect_path
            } else {
                window.location.reload()
            }
        }
    });
}

// Function to generate pagination links
function generatePaginationLinks(currentPage, totalPages, buttonsToShow) {
    const paginationLinks = [];

    // Calculate the range of buttons to display
    const startButton = Math.max(1, currentPage - Math.floor(buttonsToShow / 2));
    const endButton = Math.min(totalPages, startButton + buttonsToShow - 1);

    // Display "First" button
    // paginationLinks.push(`<li class="page-item ${startButton <= 1 ? 'disabled' : ''}"><a class="page-link" href="?page=1"><span class="fa fa-arrow-left"></span></a></li>`);
    if (startButton > 1) {
        paginationLinks.push(`<li class="page-item ${startButton > 1}"><a class="page-link" href="?page=1"><span class="fa fa-arrow-left"></span></a></li>`);
    }

    // Display page buttons within the range
    for (let i = startButton; i <= endButton; i++) {
        paginationLinks.push(`<li class="page-item ${i === currentPage ? 'active' : ''}"><a class="page-link" href="?page=${i}">${i}</a></li>`);
    }

    // Display "Last" button
    // paginationLinks.push(`<li class="page-item ${endButton >= totalPages ? 'disabled' : ''}"><a class="page-link" href="?page=${totalPages}"><span class="fa fa-arrow-right"></span></a></li>`);
    if (endButton < totalPages) {
        paginationLinks.push(`<li class="page-item"><a class="page-link" href="?page=${totalPages}"><span class="fa fa-arrow-right"></span></a></li>`);
    }

    return paginationLinks.join('');
}

function transformToTitleCase(inputString) {
    // Split the input string into words using underscores as the delimiter
    const words = inputString.split('_');

    // Capitalize the first letter of each word
    for (let i = 0; i < words.length; i++) {
        words[i] = words[i][0].toUpperCase() + words[i].slice(1);
    }

    // Join the words with a space in between
    return words.join(' ');
}

function formatDate(inputDate) {
    var datePattern = /^(0[1-9]|1[0-2])-(0[1-9]|[12][0-9]|3[01])$/;

    if (datePattern.test(inputDate)) {
        $('.submit-btn').prop('disabled', false);
        return true;
    } else {
        alert('Please enter a valid value in the MM-DD format.');
        $('.submit-btn').prop('disabled', true);
    }
}