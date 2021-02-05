/// <reference path="../TSDef/p5.global-mode.d.ts" />

"use strict";

////////////////
// PARAMS //////
////////////////

// setup
let canvasHeight;

// data
let table;
let projects = [];

// grid
let cellSize;
let numRows;
let numCols;

////////////////
// PRELOAD /////
////////////////

function preload() {
  table = loadTable("unit1MicroProjects_updated.csv", 'csv', 'header', gotData);
}

function gotData(data) {
  print("got data")
  table = data;
  for (var i = 0; i < table.getRowCount(); i++) {
    let issueDetected = table.get(i, 11);
    if (issueDetected != "true") {
      let thisProject = new Project();
      thisProject.firstName = table.get(i, 2);
      thisProject.lastName = table.get(i, 3);
      thisProject.tagLine = table.get(i, 4);
      thisProject.sketchID = table.get(i, 9);
      thisProject.p5Username = table.get(i, 10);
      thisProject.loadImage(table.get(i, 8));
      projects.push(thisProject);
    }
  }
  createGridAndDefineCanvasHeight();
}

function createGridAndDefineCanvasHeight() {

  // set min and max width for grid cell
  let minWidth = 250;
  let maxwidth = 350;

  for (let numColsIterator = 1; numColsIterator < 15; numColsIterator++) {
    let thisWidth = windowWidth / numColsIterator;
    if (thisWidth > minWidth && thisWidth < maxwidth) {
      cellSize = thisWidth;
      numCols = numColsIterator;
      break;
    }
  }

  // calculate num rows
  numRows = ceil(projects.length / numCols);
  
  // calculate canvas height
  canvasHeight = numRows * cellSize;
  
  // iterate over projects and set their
  // x and y positions
  let projectIndex = 0;
  for (let y = 0; y < canvasHeight; y += cellSize ) {
    for (let x = 0; x < windowWidth; x += cellSize) {
      // print("(" + x + ", " + y + ")");
      if (projectIndex < projects.length - 1) {
        projects[projectIndex].x = x;
        projects[projectIndex].y = y;
      }
      projectIndex++;
    }
  }
}

////////////////
// SETUP & DRAW 
////////////////
function setup() {
  createCanvas(windowWidth, canvasHeight);
  // strokeWeight(5);
}

function draw() {
  for (var i = 0; i < projects.length; i++) {
    projects[i].show();
  }
}

////////////////
// EVENTS //////
////////////////
function mouseMoved() {

  let intersectsAnyProjects = false;

  for (let i = 0; i < projects.length; i++) {
    if (projects[i].intersects()) {
      intersectsAnyProjects = true;
      break;
    } 
  }

  if (intersectsAnyProjects) {
    cursor('customCursor.png');
  } else {
    cursor('default');
  }
}
function mouseClicked() {
  for (let i = 0; i < projects.length; i++) {
    projects[i].clicked()
  }
}

////////////////
// CALL BACKS //
////////////////
function gotImage(data) {
  print("got image")
}
function imageLoadFailed(error) {
  print("error loading image: " + error.message);
}

////////////////
// CLASS ///////
////////////////
class Project {
  constructor() {
    this.firstName = "";
    this.lastName = "";
    this.tagLine = "";
    this.sketchID = "";
    this.p5Username = "";
    this.imgName = "";
    this.posterImg;

    this.x = 0;
    this.y = 0;
  }

  clicked() {
    if (this.intersects()) {
      let url = "https://editor.p5js.org/" + this.p5Username + "/full/" + this.sketchID;
      window.open(url, "_blank");
    }
  }

  intersects() {
    if (mouseX > this.x && mouseX < this.x + cellSize && mouseY > this.y && mouseY < this.y + cellSize) {
      if (this.lastName == "Adewumi") {
        print("intersects true")
      }
      return true;
    } else {
      if (this.lastName == "Adewumi") {
        print("intersects false")
      }
      return false;
    }
  }

  show() {
    image(this.posterImg, this.x, this.y, cellSize, cellSize);
    if (!this.intersects()) {
      // opacity rect while not hovering
      fill(0, 150);
      rect(this.x, this.y, cellSize);
      
      fill(255);

      // tag line while not hovering
      textAlign(CENTER, TOP);
      textSize(30);
      
      text(this.tagLine, this.x + 10, this.y + 25, cellSize - 10, cellSize - 10);

      // author while not hovering
      textAlign(CENTER, BOTTOM);
      textSize(20);
      text(this.firstName + " " + this.lastName, this.x + 10, this.y + 10, cellSize - 10, cellSize - 25);
    }
  }

  loadImage(imagePath) {
    this.posterImg = loadImage(imagePath, gotImage, imageLoadFailed)
  }

}