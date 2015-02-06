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
    var $submitLogin = $('#submit-login');
    var $submitLoginS = $('#submit-login-s');
    var $submitLogout = $('#submit-logout');
    var $password = $('#password-login');
    var $email = $('#email-login');
    var $passwordS = $('#password-login-s');
    var $emailS = $('#email-login-s');
    var $name = $('#name-login');
    var $session = $('div.session .thumbs');

    var $createSession = $('#submit-create-session');
    var $loginMessage = $('#please-login');
    var $proposeForm = $('#propose');

    var remove = function(arr, item) {
        console.log('remove_begin');
        console.log(arr);
        for(var i = arr.length; i--;) {
            if(arr[i] === item) {
                arr.splice(i, 1);
            }
        }
        console.log('remove_end');
        console.log(arr);
    }

    var set_login_status = function(logged_in, user, votes) {
        IS_LOGGED_IN = logged_in;
        USER = user;

        console.log('set_login_status_begin');
        console.log(USER_VOTES);

        $.each(votes, function(idx, v){
            if (USER_VOTES.indexOf(v) == -1){
                // Update the array of votes and serialize to pipe-separated for the cookie.
                USER_VOTES.push(v);
            } else {
                console.log('DUPLICATE!')
                console.log(v);
            }
        });

        // if (votes.length > 0) {
        //     // If there are new votes incoming, merge them.
        //     USER_VOTES = USER_VOTES.concat(votes);
        // }

        remove(USER_VOTES, "");

        console.log('set_login_status');
        console.log(USER_VOTES);

        if (logged_in) {
            $userId.html(user[1]);
            $loggedOut.hide();
            $loggedIn.show();
            $('div.'+USER[0]).addClass('mine');
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
            $('div').removeClass('mine');
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

                            console.log('create_vote_after_push');
                            console.log(USER_VOTES);

                            // Increment the count while we wait for the server to do this automatically.
                            $(thisSession).removeClass('unvoted').addClass('voted');
                            var $count_container = $('#' + session_id + ' .votes-box .count .num');
                            var old_count = parseInt($count_container.html()) + 1;
                            $count_container.html(old_count);

                            // Percolate the changes.
                            set_login_status(true, USER, USER_VOTES);

                            console.log('create_vote_after_set_login_status');
                            console.log(USER_VOTES);

                            // Update the array of votes and serialize to pipe-separated for the cookie.
                            $.cookie(cookie_namespace + 'votes', USER_VOTES.join("|"));

                            console.log('create_vote_after_cookie');
                            console.log(USER_VOTES);
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

                            console.log('remove_vote');
                            console.log(USER_VOTES);

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

    var user_login = function() {
        var url = loginHost + 'user/action/';

        var register_or_login = $(this).attr('id');
        if (register_or_login == "submit-login"){
            url += '?email=' + $email.val();
            url += '&password=' + $password.val();
            url += '&fingerprint=' + fingerprint;
            if ($name) { url += '&name=' + $name.val(); }
        } else {
            url += '?email=' + $emailS.val();
            url += '&password=' + $passwordS.val();
            url += '&fingerprint=' + fingerprint;
        }

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

                    // Redirect to main page after login
                    window.location.replace('/');
                } else {
                    alert(data.text);
                }
            }
        });
    }

    var user_logout = function() {
      $.removeCookie(cookie_namespace + 'user');
      $.removeCookie(cookie_namespace + 'votes');
      set_login_status(false, null, []);
    }

    var init = function() {
      if ($.cookie(cookie_namespace + 'user') !== undefined){
          if ($.cookie(cookie_namespace + 'votes') !== undefined) {
              set_login_status(true, $.cookie(cookie_namespace + 'user').split("|"), $.cookie(cookie_namespace + 'votes').split("|"));
          }
      } else {
          set_login_status(false, null, []);
      }
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

    $submitLogin.on('click', user_login);
    $submitLoginS.on('click', user_login);
    $submitLogout.on('click', user_logout);
    $createSession.on('click', session_create);
    $session.on('click', session_vote);
    init();
});