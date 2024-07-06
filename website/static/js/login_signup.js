document.getElementById('login-form').addEventListener('submit', function(event) {
    event.preventDefault();
    var username = document.getElementById('username').value;
    var password = document.getElementById('password').value;
    // You can add login validation logic here
    console.log('Username:', username);
    console.log('Password:', password);
});


function showSuccessPopup() {
    document.getElementById("successPopup").style.display = "block";
  }
  
  function showAlertPopup() {
    document.getElementById("alertPopup").style.display = "block";
  }
  
  function closePopup(popupId) {
    document.getElementById(popupId).style.display = "none";
  }
  