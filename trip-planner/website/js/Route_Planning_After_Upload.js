//Route planing after upload the store list
function uploadFile() {
    var file = document.getElementById('file').files[0]; //Fetch the first file uploaded by users
    // console.log(file)

    // FromData is a standard object to package the file from front-end to back-end
    var formData = new FormData();
    formData.append('file', file); // First index is key, second index is value

    // Use the JS XMLHTTPRequest(similar function as Ajax), use post method to send file to backend
    var xhr = new XMLHttpRequest(); // state 1
    // xhr.open('post', 'http://127.0.0.1:5000/clusters'); // 127.0.0.1 為本地端電腦的位置
    xhr.open('post', '/clusters'); // 127.0.0.1 為本地端電腦的位置
    xhr.send(formData); // state 2, state 3:server received the file
    // state 4:recieve response from server
    xhr.onreadystatechange = function () { // xhr was triggered by state 1 to 4
        if (this.readyState == 4 && this.status == 200) { // if state = 4 then proceed
            var cluster_data = JSON.parse(xhr.responseText);
            console.log(cluster_data)

            var map;
            var map_route;
            var num_clusters = cluster_data.length;
            Num_store_of_cluster = cluster_data[num_clusters - 1]['datas'].length //48
            var start = { lat: Number(cluster_data[num_clusters - 1]['datas'][0]['Latitude']), lng: Number(cluster_data[0]['datas'][0]['Longitude']) };
            var end = { lat: Number(cluster_data[num_clusters - 1]['datas'][Num_store_of_cluster - 1]['Latitude']), lng: Number(cluster_data[num_clusters - 1]['datas'][Num_store_of_cluster - 1]['Longitude']) };
            // console.log('Num_store_of_cluster:', Num_store_of_cluster)            
            // console.log('Num_cluster',)
            // console.log('Start_Site',start)
            // console.log('End_Site',end)


            //Initialization of maps
            function initialize() {
                // option for route planning
                // var rendererOptions = {
                //     suppressMarkers: true
                // };
                directionsService = new google.maps.DirectionsService();
                directionsDisplay = new google.maps.DirectionsRenderer({suppressMarkers: true});
                // directionsDisplay = new google.maps.DirectionsRenderer(rendererOptions);
                // Start point at the first store in the first cluster
                var startPoint = new google.maps.LatLng(cluster_data[0]['datas'][0]['Latitude'], cluster_data[0]['datas'][0]['Longitude']);
                // console.log('start_point',startPoint);
                var myOptions = {
                    zoom: 13,
                    mapTypeId: google.maps.MapTypeId.ROADMAP,
                    center: startPoint
                }
                map = new google.maps.Map(document.getElementById("map"), myOptions);
                directionsDisplay.setMap(map);


                // 初始化地圖
                map_route = new google.maps.Map(document.getElementById('map2'), {
                    zoom: 16,
                    center: { lat: 25.034010, lng: 121.562428 }
                });
    
                // 放置路線圖層
                directionsDisplay.setMap(map_route);

            }



            function calcRoute() {

                // Looping to 1.add markers to each points 2.add a waypoint list for he route of last cluster
                for (let j = 0; j < cluster_data.length; j++) {
                    var waypts = [];

                    // Have a color list for the format of markers, and put the markers
                    colors = ['red', 'blue', 'green', 'orange', 'purple', 'yellow', 'pink', 'red-dot', 'blue-dot', 'green-dot', 'orange-dot', 'purple-dot', 'yellow-dot', 'ltblue-dot', 'pink-dot', 'red', 'blue', 'green', 'orange', 'purple', 'yellow', 'pink', 'red-dot', 'blue-dot', 'green-dot', 'orange-dot', 'purple-dot', 'yellow-dot', 'ltblue-dot', 'pink-dot'] //Total: 30 colors
                    for (var i = 0; i < cluster_data[j]['datas'].length; i++) {
                        var point = cluster_data[j]['datas'][i];
                        // console.log('point:', point)
                        let url = "http://maps.google.com/mapfiles/ms/icons/";
                        // url += colors[j] + "-dot.png";
                        url += colors[j] + ".png";
                        // console.log('Longitude_point',point['Longitude'])
                        // console.log('Type_of_Longitude',typeof(point['Longitude']))

                        // add in markers for each points
                        const marker = new google.maps.Marker({
                            position: {
                                lat: Number(point['Latitude']),
                                lng: Number(point['Longitude'])
                            },
                            map,
                            title: point['NUMBER'],
                            // icon:`http://maps.google.com/mapfiles/kml/pal2/icon${j}.png`;
                            icon: {
                                url: url
                            }
                        });
                        

                        // Add in info windows
                        // console.log(point)
                        var contentString =
                            '<h4>' + 'Site ID: ' + point["NUMBER"] + '</h4>' +
                            '<div>' +
                            '<b>Postcode:</b>' +
                            point["POSTCODE"] +
                            '<br>' +
                            '<b>Latitude:</b>' +
                            point["Latitude"] +
                            '<br>' +
                            '<b>Longitude:</b>' +
                            point["Longitude"] +
                            '<div>' + '<br>' + '<button id="addsite" style="background-color: #ffd903;border-radius: 5px;">Add Site</button>';


                        const infowindow = new google.maps.InfoWindow({
                            content: contentString,
                            position: {
                                lat: Number(point['Latitude']),
                                lng: Number(point['Longitude'])
                            },
                            maxWidth: 200,
                        });


                        const infoname = new google.maps.InfoWindow({
                            content: point["ADDRESS"],
                            position: {
                                lat: Number(point['Latitude']),
                                lng: Number(point['Longitude'])
                            },
                            maxWidth: 200,
                        });

                        marker.addListener('click', function () {
                            closeOtherInfo();
                            infowindow.open(marker.get('map'), marker);
                            InforObj[0] = infowindow;
                        });


                        var InforObj = []
                        function closeOtherInfo() {
                            if (InforObj.length > 0) {
                                /* detach the info-window from the marker ... undocumented in the API docs */
                                InforObj[0].set("marker", null);
                                /* and close it */
                                InforObj[0].close();
                                /* blank the array */
                                InforObj.length = 0;
                            }
                        }

                        //新增景點功能，問題待解決
                        infowindow.addListener('domready', function () {
                            document.getElementById('addsite').addEventListener('click', function () {
                                var newlist = document.createElement('li');
                                newlist.style.backgroundColor = "lightblue"

                                var newappend = document.createElement('a');
                                newappend.setAttribute("class", "toggle");
                                newappend.setAttribute("href", "javascript:void(0);");
                                newappend.setAttribute("data-item", "item-11");
                                newappend.setAttribute("id", "newappendid");
                                var sitename = 'New Site';
                                var newappendtext = document.createTextNode(sitename);

                                var newparagraph = document.createElement("p");
                                newparagraph.setAttribute("class", "inner");
                                newparagraph.setAttribute("height", "120px");
                                newparagraph.setAttribute("weight", "120px");
                                // newparagraph.innerHTML="this is a book"
                                // var newparagraphtext=document.createTextNode("Lorem ipsum dolor sit amet, consectetur adipiscing elit. Maecenas tempus placerat")

                                newappend.appendChild(newappendtext)
                                // newparagraph.appendChild(newparagraphtext)
                                var orglist = document.getElementById('ulist');
                                orglist.appendChild(newlist);

                                newlist.appendChild(newappend);
                                newlist.appendChild(newparagraph);

                            }, false);
                        });


                        // Produce a waypoint list for route planning
                        waypts.push({
                            // location: new google.maps.LatLng(point['Latitude'], point['Longitude']),
                            location: {
                                lat: Number(point['Latitude']),
                                lng: Number(point['Longitude']),
                                NUMBER: point['NUMBER']
                            },
                            stopover: false
                        });
                        

                    }
                }

                // Draw the route based on the starting, ending and middle points(waypoints)    
                var request = {
                    origin: start,
                    destination: end,
                    waypoints: waypts,
                    optimizeWaypoints: true,
                    travelMode: google.maps.DirectionsTravelMode.WALKING,
                    // Travel modes: DRIVING, BICYCLING, TRANSIT, WALKING 
                    // departure_time:1343641500
                };

                directionsService.route(request, function (response, status) {
                    // Exceptions for route planning
                    if (status == google.maps.DirectionsStatus.OK) {
                        directionsDisplay.setDirections(response);
                    } else {
                        console.log("fail to do route planning")
                    }
                });


                console.log('waypts', waypts)

                //Add markers to route map
                var markers = [];
                for (var m = 0; m < waypts.length; m++) {
                    var url2 = 'http://maps.google.com/mapfiles/kml/paddle/'
                    flag_num = m+1
                    console.log('flag_num',flag_num)
                    url2 = url2+ flag_num + ".png";
                    console.log('waypoint lat',waypts[m]['location']['lat'])
                    markers[flag_num] = new google.maps.Marker({
                        position: {
                          lat: waypts[m]['location']['lat'],
                          lng: waypts[m]['location']['lng']
                        },
                        map: map_route,
                        title: waypts[m]['location']['NUMBER'],
                        icon: {
                            url: url2
                        }
                      });
                  }


            }

            //function to add in cluster number and storename in the store list panel
            last_cluster = cluster_data[num_clusters - 1]['datas'];
            for (var j = 0; j < last_cluster.length; j++) {
                // Add site info to the side panael
                var newlist = document.createElement('li');
                newlist.style.backgroundColor = "#F5F5F5"

                var newappend = document.createElement('a');
                newappend.setAttribute("class", "toggle");
                newappend.setAttribute("href", "javascript:void(0);");
                newappend.setAttribute("data-item", "item-11");
                newappend.setAttribute("id", "newappendid");
                var sitename = 'Site ' + String(j + 1) + ' - ' + last_cluster[j]["NUMBER"];
                var newappendtext = document.createTextNode(sitename);

                var newparagraph = document.createElement("div");
                newparagraph.setAttribute("class", "inner");
                newparagraph.setAttribute("height", "180px");
                newparagraph.setAttribute("weight", "120px");

                var newbr1 = document.createElement("div");
                newbr1.innerHTML = "ID: " + last_cluster[j]["NUMBER"]
                var newbr2 = document.createElement("div");
                newbr2.innerHTML = "Address: " + last_cluster[j]["ADDRESS"]
                var newbr3 = document.createElement("div");
                newbr3.innerHTML = "Postcode: " + last_cluster[j]["POSTCODE"]
                var newbr4 = document.createElement("div");
                newbr4.innerHTML = "latitude: " + last_cluster[j]["Latitude"]
                var newbr5 = document.createElement("div");
                newbr5.innerHTML = "longtitude: " + last_cluster[j]["Longitude"]

                newappend.appendChild(newappendtext)
                var orglist = document.getElementById('ulist');
                orglist.appendChild(newlist);

                newlist.appendChild(newappend);
                newlist.appendChild(newparagraph);
                newparagraph.appendChild(newbr1);
                newparagraph.appendChild(newbr2);
                newparagraph.appendChild(newbr3);
                newparagraph.appendChild(newbr4);
                newparagraph.appendChild(newbr5);
            }

            // function create_store_list() {
            //     for (let k = 0; k < num_clusters; k++) {
            //         document.getElementById('storelist')
            //             .insertAdjacentHTML('beforeEnd', `
            // <div onclick="open_close(event,${k})" id='cluster${k}'>Day ${k + 1}
            // <div class="cluster-close" id="inner${k}"></div>
            // </div>
            // `)
            //         // Change the color of storelist
            //         d3.select('#storelist')
            //             .style('color', 'white')

            //         for (let j = 0; j < cluster_data[k]['datas'].length; j++) {
            //             document.getElementById('inner' + k)
            //                 .insertAdjacentHTML('beforeEnd', `
            //     <div class='storename'>${cluster_data[k]['datas'][j]['Storename']}</div>
            //     `)
            //         }

            //     }
            // }



            //execute defined functions
            initialize();
            calcRoute();
            // create_store_list();

        }

    }
    if (!file) {
        return;
    }

}