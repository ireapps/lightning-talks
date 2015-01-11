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
    var $submitLogout = $('#submit-logout');
    var $password = $('#password-login');
    var $email = $('#email-login');
    var $name = $('#name-login');
    var $session = $('div.session.unvoted');

    var set_login_status = function(logged_in, user, votes) {
        IS_LOGGED_IN = logged_in;
        USER = user;

        if (votes.length > 0) {
            // If there are new votes incoming, merge them.
            USER_VOTES = USER_VOTES.concat(votes);
        }

        if (logged_in) {
            $userId.html(user[1]);
            $loggedOut.hide();
            $loggedIn.show();
            if (VOTING) {
                $('div.session.unvoted').css('cursor', 'pointer');
                votes_show();
            }
        } else {
            $loggedIn.hide();
            $loggedOut.show();
            if (VOTING) {
                votes_remove();
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
            var url = loginHost + 'vote/action/';
            var session_id = $(this).attr('id');
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

                        // Update the array of votes and serialize to pipe-separated for the cookie.
                        USER_VOTES.push(session_id);
                        $.cookie(cookie_namespace + 'votes', USER_VOTES.join("|"));

                        // Increment the count while we wait for the server to do this automatically.
                        var $count_container = $('#' + session_id + ' h3 span.count')
                        var old_count = parseInt($count_container.html()) + 1;
                        $count_container.html(old_count);

                        // Percolate the changes.
                        set_login_status(true, USER, USER_VOTES);
                    }
                }
            });

        }
    }

    var user_login = function() {
        var url = loginHost + 'user/action/';
        url += '?email=' + $email.val();
        url += '&password=' + $password.val();
        url += '&fingerprint=' + fingerprint;
        if ($name) { url += '&name=' + $name.val(); }

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

    $submitLogin.on('click', user_login);
    $submitLogout.on('click', user_logout);
    if (VOTING) {
        $session.on('click', session_vote);
    }
    init();
});