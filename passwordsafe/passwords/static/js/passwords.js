var baseUrl = "/";

$(document).ready(function() {

	// Handler for loading passwords from the server
	$('.showPassword').click(function(event) {
		event.preventDefault();
		if ($(this).text() == 'Show password') {
                        $(this).html('<img src="https://cdn.futurice.com/images/loading-inline.gif">');
			var id = $(this).parent().parent().attr('id');
			var field = $(this).next('.hiddenPassword');
                        var textfield = $(this);
			$.get(baseUrl + 'getPassword/' + id +'/', function(data) {
                           $(field).val(data).show().focus().select();
  			   $(textfield).text('Hide password');
                        });
		}
		else {
			$(this).next('.hiddenPassword').hide();
			$(this).text('Show password');
		}
		return false;
	});

	// Hide password fields
	$('.hiddenPassword').hide();
	$('.hidden_content').hide();

	// Bind edit and delete buttons to each row in passwords table
	$(".searchTable > tbody > tr").each(function(count, item) { rowCreatedCallback(item); });

        // Callback for when a table row has been created
        function rowCreatedCallback(nRow){

		// Create edit id dialog
		$('.edit', nRow).not('.initialized').addClass('initialized').click(function() {
			var editIcon = $(this);
			var id = editIcon.parent().attr('id');
			$("#modaltemp").remove();
			var $editIdDialog = $('<div id="modaltemp"></div>')
				.load(baseUrl + 'editPassword/' + id + '/', function(response, status, xhr) {
 				if (status == "error") {
					var msg = "Sorry but there was an error: ";
					alert(msg + xhr.status + " " + xhr.statusText);
  	  			} else {
					$editIdDialog.modal();
					$("#id_ldapGroup", $editIdDialog).chosen();
					$(".save", $editIdDialog).click(function() {
						var targetSystem = $("#id_targetSystem"),
							username = $("#id_username"),
							password = $("#id_password"),
							ldapGroup = $("#id_ldapGroup"),
							description = $("#id_description");
												
						var bValid = true;
		
						if (targetSystem.val().length < 1) {
							$(".targetSystemLabel").css('color', '#ff0000');
							$(".targetSystemLabel").text('Target system (required)');
							bValid = false;
						}
						else {
							$(".targetSystemLabel").css('color', '#4F4A45');
							$(".targetSystemLabel").text('Target system');						
						}
						if (username.val().length < 1) {
							$(".usernameLabel").css('color', '#ff0000');
							$(".usernameLabel").text('Username (required)');						
							bValid = false;
						}
						else {
							$(".usernameLabel").css('color', '#4F4A45');
							$(".usernameLabel").text('Username');						
						}
						if (password.val().length < 1) {
							$(".passwordLabel").css('color', '#ff0000');
							$(".passwordLabel").text('Password (required)');						
							bValid = false;
						}
						else {
							$(".passwordLabel").css('color', '#4F4A45');
							$(".passwordLabel").text('Password');								
						}
						if (ldapGroup.val().length < 1) {
							$(".ldapGroupLabel").css('color', '#ff0000');
							$(".ldapGroupLabel").text('Ldap group (required)');						
							bValid = false;
						}
						else {
							$(".ldapGroupLabel").css('color', '#4F4A45');
							$(".ldapGroupLabel").text('Ldap group with access right');							
						}																
						
						if (bValid) {
							$("#editPasswordForm").attr("action", baseUrl + 'editPassword/' + id + '/');
							$('#editPasswordForm').submit();
						}

					});

					$('.hiddenPw', $editIdDialog).hide();
					$('.showPw', $editIdDialog).click(function(event) {
						event.preventDefault();
						if ($(this).text() == 'Show password') {
							$('.hiddenPw').show();
							$(this).text('Hide password');
						}
						else {
							$('.hiddenPw').hide();
							$(this).text('Show password');
						}
						return false;
					});				
				}
			});

			return false;
	        });		
            


		// Show the delete item dialog
		$('.delete', nRow).not('.initialized').addClass('initialized').click(function() {
			var deleteIcon = $(this);
                        var id = deleteIcon.parent().attr('id');
			var $deleteDialog = $('<div class="modal"><div class="modal-header"><button class="close" data-dismiss="modal">x</button><h3>Go ahead and delete?</h3></div><div class="modal-body"><p>Are you sure you want to go ahead and delete this password?</p></div><div class="modal-footer"><a href="#" class="btn" data-dismiss="modal">Cancel</a> <a href="'+ baseUrl + 'deletePassword/' + id + '/" class="delete_button btn btn-danger">Delete</a></div></div>');
                        $deleteDialog.modal();
			return false;
		});
            return nRow
        }

	// Set headers for edit and delete
	$("#editHeader").html('Edit');
	$("#deleteHeader").html('Delete');

	
	// Toggle showing more of the description
	$('.toggle').toggle(
	function(){
		$(this).nextAll('.descContent1').toggle();
		$(this).nextAll('.descContent2').toggle();
		$(this).toggleClass('icon-minus-sign');
		$(this).toggleClass('icon-plus-sign');
	}, function(){
		$(this).nextAll('.descContent1').toggle();
		$(this).nextAll('.descContent2').toggle();
		$(this).toggleClass('icon-plus-sign');
		$(this).toggleClass('icon-minus-sign');
	});	

	// Create new password dialog
	$('#newPassword').click(function() {
                $("#modaltemp").remove();
		var $newIdDialog = $('<div id="modaltemp"></div>')
			.load(baseUrl + 'newPassword/',  function(response, status, xhr) {
                        if (status == "error") {
                             var msg = "Sorry but there was an error: ";
                             alert(msg + xhr.status + " " + xhr.statusText);
                } else {
			$newIdDialog.modal();
			// Interactive group selection list
			$("#id_ldapGroup", $newIdDialog).chosen();

			$(".save", $newIdDialog).click(function() {
				var targetSystem = $("#id_targetSystem"),
					username = $("#id_username"),
					password = $("#id_password"),
					ldapGroup = $("#id_ldapGroup"),
					description = $("#id_description");
										
				var bValid = true;
					
				// Target system validation
				if (targetSystem.val().length < 1) {
					$(".targetSystemLabel").css('color', '#ff0000');
					$(".targetSystemLabel").text('Target system (required)');
					bValid = false;
				}
				else if (targetSystem.val().length > 30) {
					$(".targetSystemLabel").css('color', '#ff0000');
					$(".targetSystemLabel").text('Target system (max 30 characters)');
					bValid = false;						
				}
				else {
					$(".targetSystemLabel").css('color', '#4F4A45');
					$(".targetSystemLabel").text('Target system');						
				}
						
				// Username validation
				if (username.val().length < 1) {
					$(".usernameLabel").css('color', '#ff0000');
					$(".usernameLabel").text('Username (required)');						
					bValid = false;
				}
				else if (username.val().length > 50) {
					$(".usernameLabel").css('color', '#ff0000');
					$(".usernameLabel").text('Username (max 50 characters)');
					bValid = false;						
				}					
				else {
					$(".usernameLabel").css('color', '#4F4A45');
					$(".usernameLabel").text('Username');						
				}

				// Password validation
				if (password.val().length < 1) {
					$(".passwordLabel").css('color', '#ff0000');
					$(".passwordLabel").text('Password (required)');						
					bValid = false;
				}
				else if (password.val().length > 50) {
					$(".passwordLabel").css('color', '#ff0000');
					$(".passwordLabel").text('Password (max 50 characters)');
					bValid = false;						
				}						
				else {
					$(".passwordLabel").css('color', '#4F4A45');
					$(".passwordLabel").text('Password');								
				}		

				// Ldap group validation
				if (ldapGroup.val().length < 1) {
					$(".ldapGroupLabel").css('color', '#ff0000');
					$(".ldapGroupLabel").text('Ldap group (required)');						
					bValid = false;
				}
				else {
					$(".ldapGroupLabel").css('color', '#4F4A45');
					$(".ldapGroupLabel").text('Ldap group with access right');							
				}

				// Description validation													
				if (description.val().length > 10000) {
					$(".descriptionLabel").css('color', '#ff0000');
					$(".descriptionLabel").text('Description (max 10000 characters)');						
					bValid = false;
				}
				else {
					$(".descriptionLabel").css('color', '#4F4A45');
					$(".descriptionLabel").text('Description');							
				}

				// If validations check out - submit form			
				if (bValid) {
                                      $('#editPasswordForm').submit();
				}
				return false;
			});

			return false;
		} // end of load else
		}); // end of load callback
	}); // end of new password click
})
