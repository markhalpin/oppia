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
 * @fileoverview Directive for the "simple editor" tab in the exploration
 * editor.
 */

// Make the last link active when the scroll reaches the bottom of the page.
oppia.value('duScrollBottomSpy', true);
// This indicates that the observed elements are the first ones in their
// respective sections (rather than the entire sections themselves).
oppia.value('duScrollGreedy', true);

oppia.directive('simpleEditorTab', [function() {
  return {
    restrict: 'E',
    templateUrl: 'editor/simpleEditorTab',
    controller: [
      '$scope', '$document', '$anchorScroll', '$window', '$timeout',
      'EditorModeService', 'explorationTitleService', 'duScrollDuration',
      'explorationStatesService',
      function(
          $scope, $document, $anchorScroll, $window, $timeout,
          EditorModeService, explorationTitleService, duScrollDuration,
          explorationStatesService) {
        $scope.setEditorModeToFull = EditorModeService.setModeToFull;
        $scope.explorationTitleService = explorationTitleService;
        $scope.fields = [];

        $scope.defaultScrollOffset = Math.max(
          100, $window.innerHeight / 2 - 100);
        $scope.scrollSpyIsActive = true;
        $window.onresize = function() {
          $scope.defaultScrollOffset = Math.max(
            100, $window.innerHeight / 2 - 100);

          // This is needed in order to reset the offsets for the scroll
          // anchors in the sidebar, until
          // https://github.com/oblador/angular-scroll/issues/179 is addressed.
          $scope.scrollSpyIsActive = false;
          $timeout(function() {
            $scope.scrollSpyIsActive = true;
          }, 5);
        };

        // Scroll the page so that the directive with the given id is in focus.
        var scrollToElement = function(directiveId) {
          $document.scrollToElementAnimated(
            angular.element(document.getElementById(directiveId)),
            $scope.defaultScrollOffset);
        };

        // Navigates to the first field that has not been filled yet, and opens
        // it.
        $scope.goForward = function() {
          for (var i = 0; i < $scope.fields.length; i++) {
            if (!$scope.fields[i].isValid()) {
              scrollToElement($scope.fields[i].id);
              $timeout(function() {
                $scope.$broadcast('externalOpen', $scope.fields[i].id);
              }, duScrollDuration);
              return;
            }
          }
        };

        $scope.$on('fieldEditorClosed', function(evt, identifier) {
          evt.stopPropagation();
          for (var i = 0; i < $scope.fields.length; i++) {
            if ($scope.fields[i].id === identifier) {
              // If the field value is not valid, scroll to the next field and
              // open it. Otherwise, return without doing anything.
              if ($scope.fields[i].isValid() && i + 1 < $scope.fields.length) {
                scrollToElement($scope.fields[i + 1].id);
                $timeout(function() {
                  $scope.$broadcast('externalOpen', $scope.fields[i + 1].id);
                }, duScrollDuration);
              }
              return;
            }
          }
        });

        $scope.$on('refreshStateEditor', function() {
          $scope.initStateEditor();
        });

        $scope.initStateEditor = function() {
          $scope.fields = [{
            id: 'titleId',
            directiveName: 'plaintext-field',
            header: 'What would you like to teach?',
            sidebarLabel: 'Title',
            getInitDisplayedValue: function() {
              return explorationTitleService.displayed;
            },
            isValid: function() {
              return !!explorationTitleService.savedMemento;
            },
            save: function(newValue) {
              explorationTitleService.displayed = newValue;
              explorationTitleService.saveDisplayedValue();
            }
          }, {
            id: 'introId',
            directiveName: 'html-field',
            header: 'Introduction',
            sidebarLabel: 'Introduction',
            getInitDisplayedValue: function() {
              return explorationStatesService.getState(
                'Introduction').content[0].value;
            },
            isValid: function() {
              return !!explorationStatesService.getState(
                'Introduction').content[0].value;
            },
            save: function(newValue) {
              // REDO to also use changeListService.
              var stateData = explorationStatesService.getState('Introduction');
              stateData.content[0].value = newValue;
              explorationStatesService.setState('Introduction', stateData);
            }
          }, {
            id: 'question1Id',
            directiveName: 'html-field',
            header: 'Question 1',
            sidebarLabel: 'Question 1',
            getInitDisplayedValue: function() {
              return explorationStatesService.getState(
                'Question 1').content[0].value;
            },
            isValid: function() {
              return !!explorationStatesService.getState(
                'Question 1').content[0].value;
            },
            save: function(newValue) {
              // REDO to also use changeListService.
              var stateData = explorationStatesService.getState('Question 1');
              stateData.content[0].value = newValue;
              explorationStatesService.setState('Question 1', stateData);
            }
          }];

          // Give the page a little while to load, then scroll so that the first
          // element is in focus.
          $timeout(function() {
            scrollToElement($scope.fields[0].id);
          }, 50);
        };
      }
    ]
  };
}]);
