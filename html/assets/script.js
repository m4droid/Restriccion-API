Object.prototype.has_key = function (key) {
  return Object.keys(this).indexOf(key) >= 0;
}

var app = angular.module('restriccionSclApp', ['ngMaterial']);

app.controller('AppCtrl', ['$scope', '$mdSidenav', '$http', function ($scope, $mdSidenav, $http) {
  $scope.toggleSidenav = function (menuId) {
    $mdSidenav(menuId).toggle();
  };

  moment.locale('es');
  $scope.today = moment();

  $scope.info = {};

  $http.get('http://restriccion-scl.m4droid.com/api/0/restricciones?fecha=' + $scope.today.format('YYYY-MM-DD')).
    success(function (data, status, headers, config) {
      if (data.length < 1) return;

      if (data[0].has_key("actualizacion")) {
        $scope.info.update_today = moment(data[0].actualizacion);
      }

      if (data[0].has_key("sin_sello_verde")) {
        $scope.info.without_green_seal_today = data[0].sin_sello_verde;
      }

      if (data[0].has_key("con_sello_verde")) {
        $scope.info.with_green_seal_today = data[0].con_sello_verde;
      }

      if (data[0].has_key("estado")) {
        $scope.info.air_quality_today = data[0].estado;
      }

      if (data[0].has_key("fuente")) {
        $scope.info.source = data[0].fuente;
      }
    });

  $http.get('http://restriccion-scl.m4droid.com/api/0/restricciones?fecha=' + moment().add(1, 'days').format('YYYY-MM-DD')).
    success(function (data, status, headers, config) {
      if (data.length < 1) return;

      if (data[0].has_key("actualizacion")) {
        $scope.info.update_tomorrow = moment(data[0].actualizacion);
      }

      if (data[0].has_key("sin_sello_verde")) {
        $scope.info.without_green_seal_tomorrow = data[0].sin_sello_verde;
      }

      if (data[0].has_key("con_sello_verde")) {
        $scope.info.with_green_seal_tomorrow = data[0].con_sello_verde;
      }

      if (data[0].has_key("estado")) {
        $scope.info.air_quality_tomorrow = data[0].estado;
      }
    });
}]);
