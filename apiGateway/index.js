const express = require('express')
const app = express()
const cors = require('cors')
const proxy = require('express-http-proxy')

const url = process.env.BOOKING_URL; 
// process.env.USER_KEY;

app.use(express.json());
app.use(express.urlencoded());
app.use(cors());

// app.use('/booking/docs', proxy('http://localhost:8000/docs'))
app.use('/booking', proxy(`http://${url}:80`))


app.get('/', (req, res) => {
    res.send('Hello World!')
})


app.listen(5000, () => {
    console.log('Server is running on port 5000')
})


