/*
 * Copyright (c) 2022.
 * The ECHOES Project (https://echoesproj.eu/) / Compass Informatics
 */

// Add debug actions to flyout menu

$(function () {
  $("[data-toggle='rst-debug-badge']").on("click", function () {
    $("[data-toggle='rst-versions']").toggleClass("rst-badge");
  });
})
