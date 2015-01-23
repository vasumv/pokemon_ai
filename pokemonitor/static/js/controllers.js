bot.controller('BotController', ['$scope', '$http', function($scope, $http) {
  $scope.bots = []
  $scope.refresh = function() {
    $scope.bots = []
    $http.get("/api/status").success(function(data) {
      for (var name in data) {
        botInfo = data[name];
        $scope.bots.push(
          {
            'name': name,
            'url': botInfo.url,
            'scores': botInfo.scores
          }
        )
      }
    });
  }
  $scope.refresh();
}]);
