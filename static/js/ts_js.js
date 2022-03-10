$(document).ready(function () {
            call_restroom_list();
        });

function call_restroom_list() {
    // {#현재 이 html이 랜딩되고있는 url 추출하기#}
    var url_string = window.location.href;
    var url = new URL(url_string);
    // {#url에서 구이름 추출하기#}
    var guname = url.href.replace("http://14.42.75.92:5000/gu_names/", "")

    $.ajax({
        type: 'GET',
        url: `/api?guname=${guname}`,
        dataType: 'json',
        data: {},
        success: function (response) {
            let rows = response["restroom_list"]
            for (i = 0; i < rows.length; i++) {
                let name = rows[i]["name"]
                let address = rows[i]["address"]
                let restroom_id = rows[i]["restroom_id"]

                let current_url = new URL(window.location.href).href
                let next_url = current_url + "/" + restroom_id

                let temp_html =`<list>
                                    <a href="${next_url}">
                                    <article class="message is-info" >
                                        <div class="message-header">
                                           <div class="rest-title"><p># ${name}</p></div>
                                            
                                        </div>
                                        <div class="message-body">
                                            <div>
                                                <strong>주소 </strong>${address}
                                            </div>
                                        </div>
                                    </article>
                                    </a>
                                </list>`

                $('#restroom_list').append(temp_html)
            }
        }})}