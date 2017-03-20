<?PHP
// mode changer for leds
// selects which script is allowed to change leds
if( isset($_POST['mode']) )
{
$mode = $_POST["mode"];

exec("sudo su - root -c \"echo $mode > /home/pi/bollocks/statusscripts/mode\"");
}
if( isset($_POST['subnet']) )
{
$subnet = $_POST["subnet"];

exec("sudo su - root -c \"echo $subnet > /home/pi/bollocks/statusscripts/subnet\"");
}
?>

<form action="/" method="post">

<h1>MODE</h1>
<select name=mode>
  <option value="1">icinga</option>
  <option value="2">random</option>
  <option value="3">network</option>
  <option value="4">kit</option>
  <option value="5">fire</option>
  <option value="6">chrismas</option>
  <option value="7">clear</option>
  <option value="8">bigdemo</option>
  <option value="9">rainbow</option>
  <option value="x">nothing</option>
</select>

<h2>Netwerk Segment</h2>
<select name=subnet>
  <option value="192.168.1">network1</option>
  <option value="192.168.2">network2</option>
</select>
<P>
  <input type="submit">
</form>
  <pre>
<?PHP
system("find /led -not -user root -exec ls -latr {} \; | awk '{ print $9\" \"$3 }' | sort  -n ");
?>
</pre>

