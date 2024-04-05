// Function to store the scroll position in local storage
  function storeScrollPosition() {
    localStorage.setItem("watchlistScrollPosition", window.scrollY);
  }

  // Function to scroll to the stored position
  function scrollToStoredPosition() {
    var scrollPosition = localStorage.getItem("watchlistScrollPosition");
    if (scrollPosition !== null) {
      window.scrollTo({ top: scrollPosition, behavior: 'auto' }); // Use behavior: 'auto' for instant scrolling
      localStorage.removeItem("watchlistScrollPosition"); // Remove the stored position after scrolling to it
    }
  }

  // Attach the storeScrollPosition function to the click event of "Add to Watchlist" and "Remove from Watchlist" buttons
  document.addEventListener("DOMContentLoaded", function() {
    var watchlistButtons = document.querySelectorAll(".add-to-watchlist-btn, .remove-from-watchlist-btn");
    for (var i = 0; i < watchlistButtons.length; i++) {
      watchlistButtons[i].addEventListener("click", storeScrollPosition);
    }

    // Scroll to the stored position after the page has fully loaded
    scrollToStoredPosition();
  });

  // Continuously store the scroll position as the user scrolls the page
  document.addEventListener("scroll", storeScrollPosition);







  document.addEventListener("DOMContentLoaded", function () {
    // Find the carousel element by its ID
    var carousel = document.getElementById("image-carousel-{{ listing.id }}");

    // Initialize the carousel using Bootstrap Carousel constructor
    var bootstrapCarousel = new bootstrap.Carousel(carousel, {
      interval: false, // Disable automatic cycling
    });

    // Remove the 'paused' class to start the carousel
    carousel.classList.remove("paused");

    // Pause the carousel when the mouse enters and resume when it leaves
    carousel.addEventListener("mouseenter", function () {
      bootstrapCarousel.pause();
    });

    carousel.addEventListener("mouseleave", function () {
      bootstrapCarousel.cycle();
    });
  });