var express = require('express');
var router = express.Router();
fs = require('fs');

/* GET home page. */
router.get('/', function(req, res) {
  res.render('index', { title: 'Express' });
});

router.get('/torrents', function(req,res){
  fs.readFile('/var/www/home_portal/public/torrent/torrent_list.json', 'utf8', function(err, data){
  	res.json(data);
  })
})
module.exports = router;
