
var directionsService = new google.maps.DirectionsService();

// Get Json file of store list with distributed clusters by machine learning
var dataUrl = "http://127.0.0.1:5000/clusters"
var xhr = new XMLHttpRequest();
xhr.open('get', dataUrl);
xhr.send(null);
xhr.onload = function () {
        var cluster_data = JSON.parse(xhr.responseText);
        console.log(cluster_data)
        console.log('Success to reload the data with clusters')
        console.log(cluster_data[0]['datas'][0]['Latitude'])

        var map;
        
        var num_clusters = cluster_data.length;
        Num_store_of_cluster = cluster_data[num_clusters-1]['datas'].length
        console.log('Num_store_of_cluster:', Num_store_of_cluster)
        var start = { lat: cluster_data[num_clusters-1]['datas'][0]['Latitude'], lng: cluster_data[0]['datas'][0]['Longitude'] };
        var end = { lat: cluster_data[num_clusters-1]['datas'][Num_store_of_cluster - 1]['Latitude'], lng: cluster_data[0]['datas'][Num_store_of_cluster - 1]['Longitude'] };
        // console.log(start)
        // console.log(end)


        //地圖初始化
        function initialize() {

                //規畫路徑呈現選項
                var rendererOptions = {
                        suppressMarkers: true
                };

                directionsDisplay = new google.maps.DirectionsRenderer(rendererOptions);
                // Start point at the first store in the first cluster
                var startPoint = new google.maps.LatLng(cluster_data[0]['datas'][0]['Latitude'], cluster_data[0]['datas'][0]['Longitude']);
                // console.log(startPoint);
                var myOptions = {
                        zoom: 14,
                        mapTypeId: google.maps.MapTypeId.ROADMAP,
                        center: startPoint
                }
                map = new google.maps.Map(document.getElementById("map"), myOptions);
                directionsDisplay.setMap(map);
        }


        //規畫路徑
        function calcRoute() {


                // // Plug the python clustering_X_features dataframe into waypts      
                // // 中繼點位置
                // var arrPoint = ['23.4520305,120.3438189', '23.379169, 120.162204',
                //         '23.4276688,120.3978147', '23.5374734,120.4361779',
                //         '23.4562847,120.3321377', '23.5619892,120.4613978',
                //         '23.451089, 120.430542', '23.2958876,120.5909089',
                //         '23.4568671,120.4748527', '23.604568,120.4003377',
                //         '23.3374553,120.2444604', '23.467152, 120.244496',
                //         '23.555779, 120.354499', '23.446775, 120.493058',
                //         '23.4507588,120.4824988', '23.4581013,120.1500569',
                //         '23.5857586,120.5530373', '23.5541796,120.3467649',
                //         '23.4345686,120.4356137', '23.336458,120.242633']

                // //經過地點 original version
                // var waypts = [];
                // for (var i = 0; i < arrPoint.length; i++) {
                //         var point = arrPoint[i].split(',');
                //         // console.log(point)
                //         waypts.push({
                //                 location: new google.maps.LatLng(point[0], point[1]),
                //                 stopover: false
                //         });

                // }

                // Plug the python clustering_X_features dataframe into waypts      
                // 中繼點位置

                // Convert the lat and long to the google map lat and long
                //經過地點 original version
                for (let j = 0; j < cluster_data.length; j++) {
                        var waypts = [];
                        colors = ['red', 'blue', 'green', 'orange', 'purple', 'yellow', 'pink', 'red-dot', 'blue-dot', 'green-dot', 'orange-dot', 'purple-dot', 'yellow-dot', 'ltblue-dot', 'pink-dot', 'red', 'blue', 'green', 'orange', 'purple', 'yellow', 'pink', 'red-dot', 'blue-dot', 'green-dot', 'orange-dot', 'purple-dot', 'yellow-dot', 'ltblue-dot', 'pink-dot']
                        for (var i = 0; i < cluster_data[j]['datas'].length; i++) {
                                var point = cluster_data[j]['datas'][i];
                                // console.log('point:', point['Longitude'])

                                let url = "http://maps.google.com/mapfiles/ms/icons/";
                                // url += colors[j] + "-dot.png";
                                url += colors[j] + ".png";

                                new google.maps.Marker({
                                        position: {
                                                lat: point['Latitude'],
                                                lng: point['Longitude']
                                        },
                                        map,
                                        title: "Hello World!",
                                        // icon:`http://maps.google.com/mapfiles/kml/pal2/icon${j}.png`;
                                        icon: {
                                                url: url
                                        }
                                });
                                waypts.push({
                                        // location: new google.maps.LatLng(point['Latitude'], point['Longitude']),
                                        location: {
                                                lat: point['Latitude'],
                                                lng: point['Longitude']
                                        },
                                        stopover: false
                                });
                        }



                        
                        
                        
                }

                //規畫路徑請求        
                var request = {
                        origin: start,
                        destination: end,
                        waypoints: waypts,
                        optimizeWaypoints: true,
                        travelMode: google.maps.DirectionsTravelMode.DRIVING,
                        //Travel modes: DRIVING, BICYCLING, TRANSIT, WALKING 
                        // departure_time:1343641500
                };

                directionsService.route(request, function (response, status) {
                        //規畫路徑回傳結果
                        if (status == google.maps.DirectionsStatus.OK) {
                                directionsDisplay.setDirections(response);
                        }
                });
                // console.log(waypts)
        }

        //function to add in cluster number and storename in the store list panel

        
        
        function create_store_list(){
                // Dataset_Array = [{
                //         'Storecode': 'Distell10166',
                //         'Storename': '7-11 太保',
                //         'Store_Address': '嘉義縣太保市後潭里後潭408-7號408-8號一樓',
                //         'Longitude': '120.344',
                //         'Latitude': '23.452',
                //         'Clusters': 20
                //       }, {
                //         'Storecode': 'Distell10169',
                //         'Storename': '7-11 布袋',
                //         'Store_Address': '嘉義縣布袋鎮興中里14鄰上海路177號',
                //         'Longitude': '120.162',
                //         'Latitude': '23.379',
                //         'Clusters': 8
                //       }];
                    
                for(let k=0;k<num_clusters;k++){
                        document.getElementById('storelist')
                        .insertAdjacentHTML('beforeEnd',`
                                <div onclick="open_close(event,${k})" id='cluster${k}'>Day ${k+1}
                                        <div class="cluster-close" id="inner${k}"></div>
                                </div>
                        `)
                        // Change the color of storelist
                        d3.select('#storelist')
                        .style('color','white')

                        for(let j=0;j<cluster_data[k]['datas'].length;j++){
                                document.getElementById('inner'+k)
                                .insertAdjacentHTML('beforeEnd',`
                                        <div class='storename'>${cluster_data[k]['datas'][j]['Storename']}</div>
                        `)
                        }
                
                }





                        // store list version 1
                        // for(let k=0;k<num_clusters;k++){
                        //         // console.log(k)
                        //         d3.select('#storelist')
                        //         .append('div')
                        //         .text('Day '+(k+1))
                        //         .style('color','white')
                        //         .attr('id','cluster'+k)
                        //         // .on('click',open_close(k))
                        //         .on('click',function(){
                        //                 console.log(k);
                        //                 var elements = document.querySelectorAll(`#cluster${k}>*`);
                        //                 console.log(elements);
                        //                 elements.forEach(element=>{
                        //                         console.log(element.class)
                        //                         if(element.classList.contains('cluster-open')){
                        //                           element.classList.remove('cluster-open')
                        //                           element.classList.add('cluster-close')
                        //                         }else{
                        //                           element.classList.remove('cluster-close')
                        //                           element.classList.add('cluster-open')
                        //                         }
                        //                 });
                                        
                        //         })
                        //         for(l=0;l<cluster_data[k]['datas'].length;l++){
                        //                 d3.select('#cluster'+k)
                        //                 .append('div')
                        //                 .text(cluster_data[k]['datas'][l]['Storename'])
                        //                 .style('margin-left','10px')
                        //                 .attr('class','cluster-close')
                        //                 .classed('storename', true)
                        //         }
                        // }
        }

        //execute defined functions
        initialize();
        calcRoute();
        create_store_list();
        // open_close()

}