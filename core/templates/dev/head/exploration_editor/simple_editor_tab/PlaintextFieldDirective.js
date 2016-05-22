// Copyright 2014 The Oppia Authors. All Rights Reserved.
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//      http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS-IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

/**
 * @fileoverview Directive for a plain-text field in the simple editor view.
 */

oppia.directive('plaintextField', [function() {
  return {
    restrict: 'E',
    templateUrl: 'editor/plaintextField',
    scope: {
      displayedValue: '=',
      identifier: '@',
      onFinishEditing: '&'
    },
    controller: ['$scope', 'focusService', function($scope, focusService) {
      $scope.inEditMode = false;
      $scope.focusLabel = focusService.generateFocusLabel();

      $scope.$on('externalOpen', function(evt, identifier) {
        if (identifier === $scope.identifier) {
          $scope.startEditing();
        }
      });

      $scope.startEditing = function() {
        $scope.inEditMode = true;
        focusService.setFocus($scope.focusLabel);
      };

      $scope.finishEditing = function() {
        $scope.inEditMode = false;
        $scope.onFinishEditing();
        $scope.$emit('fieldEditorClosed', $scope.identifier);
      };

      $scope.onKeypress = function(evt) {
        if (evt.keyCode === 13) {
          $scope.finishEditing();
        }
      };
    }]
  };
}]);
