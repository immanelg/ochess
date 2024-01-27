// Yes. I know. we don't care about security right now. I will do OAuth2 some day, not today.
const key = "user_id";
export let userId = localStorage.getItem(key)
if (!userId) {
  userId ??= Math.random() * Math.pow(2, 64);
  localStorage.setItem(key, userId);
}
