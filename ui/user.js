// @ts-check

// Yes. I know. we don't care about security right now. I will do OAuth2 some day, not today.
/** @type {number} */
export let userId;

const key = "user_id";
const storedId = localStorage.getItem(key);
if (storedId === null) {
  userId = Math.ceil(Math.random() * 2147483647);
  localStorage.setItem(key, userId.toString());
} else {
  userId = parseInt(storedId);
}
