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
 * @fileoverview Directive for an interaction selector in the simple editor
 * view.
 */

oppia.directive('interactionSelector', [function() {
  return {
    restrict: 'E',
    templateUrl: 'editor/interactionSelector',
    scope: {
      initDisplayedValue: '&',
      identifier: '@',
      onFinishEditing: '='
    },
    controller: ['$scope', function($scope) {
      $scope.INTERACTION_DETAILS_LIST = [{
        id: 'MultipleChoiceInput',
        description: 'Multiple choice'
      }];

      $scope.displayedInteractionId = $scope.initDisplayedValue();

      $scope.saveNewInteractionId = function() {
        if ($scope.initDisplayedValue() !== $scope.displayedInteractionId) {
          // TODO(sll): Show a warning if this change will result in response
          // data being lost.
          var thisVariableIsHereJustToCircumventEmptyBlockWarning;
        }
        $scope.onFinishEditing($scope.displayedInteractionId);
      };
    }]
  };
}]);
