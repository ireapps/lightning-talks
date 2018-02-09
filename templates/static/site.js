$(function(){
    var VOTING = {{ VOTING|lower }};

    var IS_LOGGED_IN = false;
    var USER = [];
    var USER_VOTES = [];
    var loginHost = '/api/';
    var cookie_namespace = 'nicar15lightningtalks-';
    var fingerprint = new Fingerprint({canvas: true}).get();

    var $loggedIn = $('#logged-in');
    var $loggedOut = $('#logged-out');
    var $userId = $('#user-id');
    var $submitNew = $('#submit-new');
    var $submitExisting = $('#submit-existing');
    var $submitLogout = $('#submit-logout');
    var $password = $('#password-new');
    var $email = $('#email-new');
    var passwordExisting = $('#password-existing');
    var $emailExisting = $('#email-existing');
    var $name = $('#name-new');
    var $session = $('div.session .thumbs');

    var $createSession = $('#submit-create-session');
    var $loginMessage = $('#please-login');
    var $proposeForm = $('#propose');

    var remove = function(arr, item) { for (var i = arr.length; i--;) { if(arr[i] === item) { arr.splice(i, 1); } } }

    var set_login_status = function(logged_in, user, votes) {
        IS_LOGGED_IN = logged_in;
        USER = user;

        $.each(votes, function(idx, v){ if (USER_VOTES.indexOf(v) == -1){ USER_VOTES.push(v); } });

        remove(USER_VOTES, "");

        if (logged_in) {
            $userId.html(user[1]);
            $loggedOut.hide();
            $loggedIn.show();
            if (VOTING) {
                $('div.session.unvoted .thumbs').css('cursor', 'pointer');
                votes_show();
            } else {
                $loginMessage.hide();
                $proposeForm.show();
            }
        } else {
            $loggedIn.hide();
            $loggedOut.show();
            if (VOTING) {
                votes_remove();
            } else {
                $loginMessage.show();
                $proposeForm.hide();
            }
        }
    }

    var votes_show = function() {
        $.each(USER_VOTES, function(idx, v){
            $('#' + v).removeClass('unvoted').addClass('voted');
        });
    }

    var votes_remove = function() {
        $.each($('div.session'), function(idx, v){
            $(v).removeClass('voted').addClass('unvoted');
        });
    }

    var session_vote = function() {
        if (IS_LOGGED_IN && USER) {
            var thisSession = $(this).parent('.votes-box').parent('.session');
            var voted = $(thisSession).hasClass('voted');
            var session_id = $(thisSession).attr('id');

            if (!voted){
                var url = loginHost + 'vote/action/';
                url += '?user=' + USER[0];
                url += '&session=' + session_id;
                $.ajax(url, {
                    async: true,
                    cache: true,
                    crossDomain: false,
                    dataType: 'json',
                    jsonp: false,
                    success: function(data) {
                        if (data['success'] === true) {

                            if (USER_VOTES.indexOf(session_id) == -1){
                                // Update the array of votes and serialize to pipe-separated for the cookie.
                                USER_VOTES.push(session_id);
                            }

                            // Increment the count while we wait for the server to do this automatically.
                            $(thisSession).removeClass('unvoted').addClass('voted');
                            var $count_container = $('#' + session_id + ' .votes-box .count .num');
                            var old_count = parseInt($count_container.html()) + 1;
                            $count_container.html(old_count);

                            // Percolate the changes.
                            set_login_status(true, USER, USER_VOTES);

                            // Update the array of votes and serialize to pipe-separated for the cookie.
                            $.cookie(cookie_namespace + 'votes', USER_VOTES.join("|"));

                        }
                    }
                });
            } else {
                var url = loginHost + 'vote/action/';
                url += '?user=' + USER[0];
                url += '&session=' + session_id;
                $.ajax(url, {
                    async: true,
                    cache: true,
                    crossDomain: false,
                    dataType: 'json',
                    jsonp: false,
                    success: function(data) {
                        if (data['success'] === true) {

                            remove(USER_VOTES, session_id);

                            // Increment the count while we wait for the server to do this automatically.
                            $(thisSession).removeClass('voted').addClass('unvoted');
                            var $count_container = $('#' + session_id + ' .votes-box .count .num');
                            var old_count = parseInt($count_container.html()) - 1;
                            $count_container.html(old_count);

                            // Percolate the changes.
                            set_login_status(true, USER, USER_VOTES);

                            // Update the array of votes and serialize to pipe-separated for the cookie.
                            $.cookie(cookie_namespace + 'votes', USER_VOTES.join("|"));

                        }
                    }
                });
            }
        }
    }

    var user_login = function(register) {
        var url = loginHost + 'user/action/';

        if (register){
            url += '?email=' + $email.val();
            url += '&password=' + $password.val();
            url += '&fp=' + fingerprint;
            url += '&name=' + $name.val();
        } else {
            url += '?email=' + $emailExisting.val();
            url += '&password=' + passwordExisting.val();
            url += '&fp=' + fingerprint;
        }

        var checked = $('#going-to-nicar').is(":checked");

        if (!register || register && checked){
            $.ajax(url, {
                async: true,
                cache: true,
                crossDomain: false,
                dataType: 'json',
                jsonp: false,
                success: function(data) {
                    if (data['success'] === true) {
                        $.cookie(cookie_namespace + 'user', data['_id'] + '|' + data['name']);

                        // Votes come back as pipe-delimited from the server.
                        $.cookie(cookie_namespace + 'votes', data['votes']);
                        set_login_status(true, [data['_id'],data['name']], data['votes'].split("|"));

                    } else {
                        alert(data.text);
                    }
                }
            });

        } else {
            alert("Please do not pitch or vote unless you are going to NICAR this year!");
        }
    }

    var user_logout = function() {
        $('.instructions').remove();
        $('#sort-options').remove();
        $.removeCookie(cookie_namespace + 'user');
        $.removeCookie(cookie_namespace + 'votes');
        set_login_status(false, null, []);
    }

    var session_create = function() {
        if (IS_LOGGED_IN && USER) {
            var s = {}
            s['title'] = $proposeForm.find('input').val();
            s['description'] = $proposeForm.find('textarea').val();
            s['user'] = USER[0];

            if ($.trim(s.title) == "" || $.trim(s.description) == "") {
                alert('Please fill out the title and the description fields.')
            } else {
                var url = loginHost + 'session/action/';
                url += '?user=' + s.user;
                url += '&title=' + s.title;
                url += '&description=' + s.description;
                $.ajax(url, {
                    async: true,
                    cache: true,
                    crossDomain: false,
                    dataType: 'json',
                    jsonp: false,
                    success: function(data) {
                        if (data['success'] === true) {
                            $proposeForm.find('input').val('');
                            $proposeForm.find('textarea').val('');
                            alert('Your session "'+s.title+'" has been submitted.');
                        }
                    }
                });

            }
        } else {
            alert('Please log in or create an account.');
        }
    }

    var init = function() {
      if ($.cookie(cookie_namespace + 'user') !== undefined){
          if ($.cookie(cookie_namespace + 'votes') !== undefined) {
              set_login_status(true, $.cookie(cookie_namespace + 'user').split("|"), $.cookie(cookie_namespace + 'votes').split("|"));
          }
      } else {
          set_login_status(false, null, []);
      }

      if (!IS_LOGGED_IN){
        $('.instructions').remove();
        $('#sort-options').remove();
      }
    }

    var register_user = function() { user_login(true); }
    var login_user = function() { user_login(false); }

    $submitNew.on('click', register_user);
    $submitExisting.on('click', login_user);
    $submitLogout.on('click', user_logout);
    $createSession.on('click', session_create);
    $session.on('click', session_vote);
    init();
});