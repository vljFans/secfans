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