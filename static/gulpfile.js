'use strict'

const
  gulp = require('gulp'),
  browserify = require('gulp-browserify')

gulp.task('browserify', function () {
  return gulp
    .src('./js/index.js')
    .pipe(browserify())
    .pipe(gulp.dest('./bin/js'))
})

gulp.task('watch', function () {
  gulp.watch(['./**/*.js'], ['browserify'])
})
