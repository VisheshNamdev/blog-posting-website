document.addEventListener('DOMContentLoaded', function () {
  // Code for handling report popups
  const openReportPopupBtns = document.querySelectorAll('.report');
  const reportPopup = document.getElementById('reportPopup');
  const closeReportPopupBtn = document.getElementById('closeReportPopupBtn');
  const reportForm = document.getElementById('reportForm');
  const blogIdInput = document.getElementById('blogId');

  openReportPopupBtns.forEach(btn => {
    btn.addEventListener('click', (event) => {
      const postId = event.currentTarget.getAttribute('id').replace('report-', '');
      openReportPopup(postId);
    });
  });

  function openReportPopup(blogId) {
    blogIdInput.value = blogId;
    reportPopup.classList.remove('hidden');
  }

  closeReportPopupBtn.addEventListener('click', () => {
    reportPopup.classList.add('hidden');
  });

  // Close the popup when clicking outside of the popup content
  window.addEventListener('click', (event) => {
    if (event.target === reportPopup) {
      reportPopup.classList.add('hidden');
    }
  });

  reportForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const formData = new FormData(reportForm);
    try {
      const response = await fetch('/url/to/submit/report', {
        method: 'POST',
        body: formData
      });
      if (response.ok) {
        alert('Report submitted successfully!');
        reportPopup.classList.add('hidden');
        // You may want to refresh or update the UI here if needed
      } else {
        alert('Failed to submit report. Please try again later.');
      }
    } catch (error) {
      console.error('Error submitting report:', error);
      alert('An error occurred. Please try again later.');
    }
  });

  document.querySelectorAll('.kebabMenuButton').forEach(button => {
    button.addEventListener('click', (event) => {
        event.stopPropagation();
        const dropdownMenu = button.nextElementSibling;
        document.querySelectorAll('.dropdownMenu').forEach(menu => {
            if (menu !== dropdownMenu) {
                menu.style.display = 'none';
            }
        });
        dropdownMenu.style.display = dropdownMenu.style.display === 'block' ? 'none' : 'block';
    });
});

// Close dropdowns when clicking outside
document.addEventListener('click', (event) => {
    if (!event.target.closest('.thumb')) {
        document.querySelectorAll('.dropdownMenu').forEach(menu => {
            menu.style.display = 'none';
        });
    }
});

  // Function for confirming delete (if needed)
  function confirmDelete() {
    return confirm('Are you sure you want to delete this post?');
  }
});